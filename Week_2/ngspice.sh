#!/bin/bash

for i in {1..200}
do
  ngspice -b  eg.cir
done
