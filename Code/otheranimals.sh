#! /bin/bash

## load/download the reference sequence from the given address
## load/download the vcf file specified by the user
## then build the alignment, or further build the tree

## Usage: ./otheranimals.sh refaddress vcfaddress chr start end num raxML fastTree


## address for the reference sequence,  in XX.fa.gz
refaddress=$1
## address for your vcf file.
vcfaddress=$2

## change this to your chromosome number
chr=$3
## change this to the start position of your region
start=$4
## change this to the end position of your region
end=$5
## How many species do you have?
num=$6

## Do you want to build the tree using raxML?
raxML=$7
## Do you want to build the tree using fastTree?
fastTree=$8


echo "The region of your interest: chr"$chr":"$start"-"$end". Have fun!"
echo $refaddress $vcfaddress
echo $num $raxML $fastTree

mkdir ../../../VCFtoTree_Output_otherSpecies

## prepare reference sequence for your chosen chromosome
if [[ $refaddress == *"http://"* ]]
then
    /usr/local/bin/wget $refaddress
    filenameFaGz=$(basename "$refaddress")
    mv $filenameFaGz chr$chr.fa.gz

else
    mv $refaddress chr$chr.fa.gz
fi

gunzip -c chr$chr.fa.gz > chr$chr.fa
/usr/local/bin/samtools faidx chr$chr.fa
/usr/local/bin/samtools faidx chr$chr.fa chr$chr:$start-$end > REF_chr$chr.START$start.END$end.fa

ref=REF_chr$chr.START$start.END$end.fa

## prepare vcf file for the given region
if [[ $vcfaddress == *"http://"* ]]
then
    /usr/local/bin/wget $vcfaddress
    filenameVcfGa=$(basename "$vcfaddress")
    mv $filenameVcfGa chr$chr.vcf.gz
else
    mv $vcfaddress chr$chr.vcf.gz
fi

/usr/local/bin/tabix -h -f chr$chr.vcf.gz
/usr/local/bin/tabix -h -f chr$chr.vcf.gz $chr:$start-$end > otherAnimal_chr$chr.START$start.END$end.vcf

vcffile=otherAnimal_chr$chr.START$start.END$end.vcf


## building the alignment
python Code/vcf2fasta_otheranimals.py $vcffile $ref $start $end $num ALI_otherAnimals.fa log.txt &
wait

echo "vcftofasta has run."

## Tree building

## If use FastTree
## If the user need to compile it:
if [ $fastTree -eq 1 ]
then
    gcc -DUSE_DOUBLE -O3 -finline-functions -funroll-loops -Wall -o FastTree FastTree.c -lm
    chmod +x Code/FastTree
    Code/FastTree -gtr -gamma -nt ALI_otherAnimals.fa > FastTree_ALI_otherAnimals.newick &
    wait
fi

if [ $raxML -eq 1 ]
then
    ## If use RAxML
    python Code/fas2phy.py ALI_otherAnimals.fa ALI_otherAnimals.phy
    chmod +x Code/raxmlHPC-PTHREADS-SSE3
    Code/raxmlHPC-PTHREADS-SSE3 -T 2 -n YourRegion -s ALI_otherAnimals.phy -mGTRGAMMA -p 235 -N 2 &
    wait
    mv RAxML_bestTree.YourRegion RAxML_bestTree.YourRegion.newick &
    wait
fi

open ../../../VCFtoTree_Output/

echo "All done"
