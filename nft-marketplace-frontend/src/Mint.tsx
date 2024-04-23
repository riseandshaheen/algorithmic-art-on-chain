// Copyright 2022 Cartesi Pte. Ltd.

// Licensed under the Apache License, Version 2.0 (the "License"); you may not
// use this file except in compliance with the License. You may obtain a copy
// of the license at http://www.apache.org/licenses/LICENSE-2.0

// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
// WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
// License for the specific language governing permissions and limitations
// under the License.

import { BigNumber, ethers } from "ethers";
import React, { useEffect, useState } from "react";
import { useRollups } from "./useRollups";
import { useReportsQuery, useVoucherQuery } from "./generated/graphql";
import { Card, CardHeader, CardBody, CardFooter, Image, Stack, Heading } from '@chakra-ui/react'
import {
    Table,
    Thead,
    Tbody,
    Tfoot,
    Tr,
    Th,
    Td,
    TableCaption,
    TableContainer,
    Button,
    Text,
    Spinner,
    SimpleGrid,
    Box,
    Flex,
    Spacer,
    Grid
  } from '@chakra-ui/react'

type Report = {
    id: string;
    index: number;
    input: any, //{index: number; epoch: {index: number; }
    payload: string;
};

type Voucher = {
    id: string;
    index: number;
    destination: string;
    input: any, //{index: number; epoch: {index: number; }
    payload: string;
    proof: any;
    executed: any;
};
type IMintPropos = {
    dappAddress: string
}
type LoadingStates = {
    [key: string]: boolean;
  };

export const Mint: React.FC<IMintPropos> = (propos) => {
    const [result,reexecuteQuery] = useReportsQuery();
    const { data, fetching, error } = result;

    const [ voucherToExecute, setVoucherToExecute ] = useState(0)
    const [executionStatus, setExecutionStatus] = useState(false)
    const [voucherResult, reexecuteVoucherQuery] = useVoucherQuery({variables: { voucherIndex: 0, inputIndex: voucherToExecute }});
    const [loadingStates, setLoadingStates] = useState<LoadingStates>({});

    const rollups = useRollups(propos.dappAddress);

    if (fetching) return <p>Loading...</p>;
    if (error) return <p>Oh no... {error.message}</p>;

    if (!data || !data.reports) return <p>No reports</p>;

    const reports: Report[] = data.reports.edges.map((node: any) => {
        const n = node.node;
        let inputPayload = n?.input.payload;
        if (inputPayload) {
            try {
                inputPayload = ethers.utils.toUtf8String(inputPayload);
            } catch (e) {
                inputPayload = inputPayload + " (hex)";
            }
        } else {
            inputPayload = "(empty)";
        }
        let payload = n?.payload;
        if (payload) {
            try {
                payload = ethers.utils.toUtf8String(payload);
            } catch (e) {
                payload = payload + " (hex)";
            }
        } else {
            payload = "(empty)";
        }
        return {
            id: `${n?.id}`,
            index: parseInt(n?.index),
            payload: `${payload}`,
            input: n ? {index:n.input.index,payload: inputPayload} : {},
        };
    }).sort((b: any, a: any) => {
        if (a.input.index === b.input.index) {
            return b.index - a.index;
        } else {
            return b.input.index - a.input.index;
        }
    });

    const executeVoucher = async (index: number) => {
        if (rollups) {
        try {
            // fetch voucher with the index
            console.log("input index: ", index)
            setVoucherToExecute(index);
            reexecuteVoucherQuery({ requestPolicy: 'network-only' });

            console.log("Voucher fetched: ", voucherResult.data);
            const voucherFetched = voucherResult.data?.voucher;
            console.log("voucher to use:::", voucherFetched)
            if (voucherFetched?.proof){
                console.log("Proof found, calling smart contract")
                const tx = await rollups.dappContract.executeVoucher( voucherFetched.destination, voucherFetched.payload, voucherFetched.proof );
                const receipt = await tx.wait();
                setExecutionStatus(true)
                console.log("Voucher execution result: ", receipt.events)
            }
            else{
                console.log("No proof yet!")
            }

        } catch (e) {
            console.log(`COULD NOT EXECUTE VOUCHER: ${JSON.stringify(e)}`);
        }
        }
    }

    const handleExecuteVoucherClick = (index: any) => {
        toggleLoadingState(index, true);
        
        setTimeout(() => {
            toggleLoadingState(index, false);
            executeVoucher(index);
        }, 2000); 
      };
    
    // Function to toggle loading state for a specific card
    const toggleLoadingState = (cardId: number, isLoading: boolean) => {
        setLoadingStates((prevLoadingStates) => ({
        ...prevLoadingStates,
        [cardId]: isLoading,
        }));
    };

    return (
        <div>
            {/* List all reports */}
            <Grid templateColumns='repeat(3, 1fr)' gap={6}>
            {reports.map((n: any) => (
                <Card maxW='sm' marginBottom='5' key={`${n.input.index}-${n.index}`}>
                    {/* <Td>{n.input.index}</Td>
                    <Td>{n.index}</Td> */}
                    {/* <td>{n.input.payload}</td> */}

                    <CardBody color={'grey'}>
                                <Image
                                src={`data:image/png;base64, ${n.payload}`}
                                borderRadius='lg'
                                />
                        <Text>{n.input.index}</Text>
                    </CardBody>
                    <CardFooter>
                        <Button onClick={() => handleExecuteVoucherClick(`${n.input.index}-${n.index}`)} > {loadingStates[`${n.input.index}-${n.index}`] ? <Spinner />: "Mint"}</Button>
                    </CardFooter>
                </Card>
            ))}
            </Grid>
        </div>

    );
};
