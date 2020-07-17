#! /bin/bash
## using the vcf files and the human refernce genome
## obtain the alignment for the any region for individuals from 1000 genomes phase 3.

## Usage: ./build_tree.sh #1:chr #2:start #3:end #4:specieslist #5:vcfaddress #6:numberofSpecies #7:populationlist #8:raxML #9:fastTree

## change this to your chromosome number
chr=$1
## change this to the start position of your region
start=$2
## change this to the end position of your region
end=$3

## Takes in string of selected species returned from python GUI
specieslist=$4

## address for your vcf file.
vcfaddress=$5
num=$6

## Takes in string of selected populations returned from python GUI
populationlist=$7

## Do you want to build the tree using raxML?
raxML=$8
## Do you want to build the tree using fastTree?
fastTree=$9

# Load configuration files
. vtt.config
# Global vars
bin_fast_tree=../Code/FastTree
############################
# Function Definitions
############################

# Run RaXML
func_run_raxml(){
  echo "-------------------------"
  echo "func_run_raxml() start"
  rm ALI_final.phy
  python ../Code/fas2phy.py ALI_final.fa ALI_final.phy
  raxmlHPC-PTHREADS -T $ra_xml_threads -n YourRegion -s ALI_final.phy -mGTRGAMMA -p 235 -N 2 &
  wait
  mv RAxML_bestTree.YourRegion RAxML_bestTree.YourRegion.newick &
  wait
  echo "func_run_raxml() end"
  echo "-------------------------"
}

# Builds fasttree source code
func_build_fasttree(){
  echo "-------------------------"
  echo "func_build_fasttree() start"
  if [[ ! -f $bin_fast_tree ]]
  then
    gcc -DUSE_DOUBLE -O3 -finline-functions -funroll-loops -Wall -o ../Code/FastTree ../Code/FastTree.c -lm
  else
    echo $bin_fast_tree " file available no need to compile"
  fi
  echo "func_build_fasttree() end"
  echo "-------------------------"
}

# Runs fasttree
func_run_fasttree(){
  echo "-------------------------"
  echo "func_run_fasttree() start"

  input_file=$1
  output_file=$2

  func_build_fasttree
  chmod +x $bin_fast_tree

  ../Code/FastTree -gtr -gamma -nt $input_file > $output_file

  echo "../Code/FastTree -gtr -gamma -nt $input_file > $output_file"
  echo "func_run_fasttree() end"
  echo "-------------------------"
}

############################

mkdir $conf_dir_output
cd $conf_dir_output

echo "==================================="
echo "Working directory: " $conf_dir_output
echo "The script does not download already downloaded files"
echo "The region of your interest: chr"$chr":"$start"-"$end" for 1000 Genomes "$populationlist" population(s)"
echo "Population List: " $populationlist
echo "Species List: " $specieslist
echo "==================================="
## STEP 1
## prepare reference sequence for your chosen chromosome
# Check if file exist
if [[ ! -f chr$chr.fa.gz ]]
then
   wget http://hgdownload.soe.ucsc.edu/goldenPath/hg19/chromosomes/chr$chr.fa.gz
else
  echo " file exists no need to download chr$chr.fa.gz again, you can delete this file if you want to redownload it again"
fi

[[ ! -f chr$chr.fa ]] && gunzip -c chr$chr.fa.gz > chr$chr.fa


ref=REF_chr$chr.START$start.END$end.fa

if [[ ! -f $ref ]]
then
  samtools faidx chr$chr.fa
  samtools faidx chr$chr.fa chr$chr:$start-$end > REF_chr$chr.START$start.END$end.fa
else
  echo $ref " file exists no need to reindex, you can delete this file if you want to run indexing again"
fi

## STEP 2
##Human Condition Met


##If array contains human 1000 Genomes
## prepare 1000 genome vcf file
if [[ $specieslist == *'Human-1000Genomes'* ]]
then
    vcffile=chr$chr.START$start.END$end.vcf
    if [[ ! -f $vcffile ]]
    then
       tabix -h -f http://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.chr$chr.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz $chr:$start-$end > $vcffile
    else
      echo " file exists $vcffile no need to run tabix, you can delete this file if you want to run tabix again"
    fi

    python ../Code/vcf2fasta_erica.py $vcffile $ref $start $end $populationlist ALI_1000HG.fa log.txt &
    wait
    echo "vcftofasta has run."
fi


##If array only contains human
if [[ $specieslist = 'Human-1000Genomes' ]]
then
	 ## Tree building
  if [ $fastTree -eq 1 ]
  then
    ## If use FastTree
    func_run_fasttree ALI_1000HG.fa FastTree_ALI_1000HG.newick
  fi

  if [ $raxML -eq 1 ]
  then
    ## If use RAxML
    echo "**** calling func_run_raxml() ****"
    func_run_raxml
  fi

	open $conf_dir_output/

## Else if other species selected
else
	touch ALI_altainean.fa
	touch ALI_vindijanean.fa
	touch ALI_den.fa
	touch ALI_panTro4Ref_hg19.fa
	touch ALI_rheMac3Ref_hg19.fa
	touch ALI_customized_human.fa


    ##If array contains human-customized
    if [[ $specieslist == *'Human-Custom'* ]]
    then
        if [[ $vcfaddress == *"http://"* ]]
        then
            wget $vcfaddress
            filenameVcfGz=$(basename "$vcfaddress")
            mv $filenameVcfGz customized_human_chr$chr.vcf.gz
        else
            mv $vcfaddress customized_human_chr$chr.vcf.gz
        fi

        tabix -h -f customized_human_chr$chr.vcf.gz
        tabix -h -f customized_human_chr$chr.vcf.gz $chr:$start-$end > customized_human_chr$chr.START$start.END$end.vcf

        customizedHuman=customized_human_chr$chr.START$start.END$end.vcf

        ## building the alignment
        python ../Code/vcf2fasta_otheranimals.py $customizedHuman $ref $start $end $num ALI_customized_human.fa log.txt &
        wait
        echo "vcftofasta for customized human has run."
    fi


    ##If neadertal in array
	if [[ $specieslist == *"Neanderthal"* ]]
	then
		## prepare Altai neanderthal vcf files
		wget http://cdna.eva.mpg.de/neandertal/altai/AltaiNeandertal/VCF/AltaiNea.hg19_1000g.$chr.mod.vcf.gz
		tabix -h -f AltaiNea.hg19_1000g.$chr.mod.vcf.gz
		tabix -h -f AltaiNea.hg19_1000g.$chr.mod.vcf.gz $chr:$start-$end > Altainean_chr$chr.START$start.END$end.vcf

		vcffile_altainean=Altainean_chr$chr.START$start.END$end.vcf

		python ../Code/vcf2fasta_AltaiNean_Den_rmhetero_erica.py $vcffile_altainean $ref $start $end ALI_altainean.fa Indels_Altai.txt
	fi

    ##If Vindija neanderthal in array
    if [[ $specieslist == *"Vindija"* ]]
    then
        ## prepare Vindija vcf file
	## not gonna work until published.
        ##DO NOT USE!!!##wget http://cdna.eva.mpg.de/neandertal/Vindija/VCF/Vindija33.19/chr$chr\_mq25_mapab100.vcf.gz
        touch chr$chr\_mq25_mapab100.vcf.gz
	      tabix -h -f chr$chr\_mq25_mapab100.vcf.gz
        tabix -h -f chr$chr\_mq25_mapab100.vcf.gz $chr:$start-$end >  Vindijanean_chr$chr.START$start.END$end.vcf

        vcffile_vindijanean=Vindijanean_chr$chr.START$start.END$end.vcf

        python ../Code/vcf2fasta_AltaiNean_Den_rmhetero_erica.py $vcffile_vindijanean $ref $start $end ALI_vindijanean.fa Indels_Vindija.txt
    fi


    ##If denisova in array
	if [[ $specieslist == *"Denisova"* ]]
	then
		## prepare Denisovan vcf files
		tabix -h -f http://cdna.eva.mpg.de/neandertal/altai/Denisovan/DenisovaPinky.hg19_1000g.$chr.mod.vcf.gz $chr:$start-$end > Den_chr$chr.START$start.END$end.vcf

		vcffile_den=Den_chr$chr.START$start.END$end.vcf

		python ../Code/vcf2fasta_AltaiNean_Den_rmhetero_erica.py $vcffile_den $ref $start $end ALI_den.fa Indels_Denisova.txt
	fi

    ##If chimp in array
	if [[ $specieslist == *"Chimp"* ]]
	then
		# getting Chimpanzee(panTro4) reference, mapped to hg19
		wget http://hgdownload.soe.ucsc.edu/goldenPath/hg19/vsPanTro4/axtNet/chr$chr.hg19.panTro4.net.axt.gz
		gunzip -c chr$chr.hg19.panTro4.net.axt.gz > chr$chr.hg19.panTro4.net.axt
		python ../Code/Map_panTro4Ref2hg19.py chr$chr.hg19.panTro4.net.axt $chr $start $end ALI_panTro4Ref_hg19.fa
	fi

    ##If RM in array
	if [[ $specieslist == *"Rhesus-macaque"* ]]
	then
		# getting Rhesus(RheMac3) reference, mapped to hg19
		wget http://hgdownload.soe.ucsc.edu/goldenPath/hg19/vsRheMac3/axtNet/chr$chr.hg19.rheMac3.net.axt.gz
		gunzip -c chr$chr.hg19.rheMac3.net.axt.gz > chr$chr.hg19.rheMac3.net.axt
		python ../Code/Map_rheMac3Ref2hg19.py chr$chr.hg19.rheMac3.net.axt $chr $start $end ALI_rheMac3Ref_hg19.fa
	fi


	##May cause error if not found
	# add gaps from log.txt
	cat ALI_customized_human.fa ALI_altainean.fa ALI_vindijanean.fa ALI_den.fa ALI_panTro4Ref_hg19.fa ALI_rheMac3Ref_hg19.fa >> ALI_temp.fa
	#rm ALI_altainean.fa
	#rm ALI_vindijanean.fa
	#rm ALI_den.fa
	#rm ALI_panTro4Ref_hg19.fa
	#rm ALI_rheMac3Ref_hg19.fa
	python ../Code/add_gap.py ALI_temp.fa log.txt $start $end ALI_othergenomes_wgap.fa

	cat ALI_othergenomes_wgap.fa ALI_1000HG.fa >> ALI_final.fa
	rm ALI_temp.fa


    if [ $fastTree -eq 1 ]
    then
      ## If use FastTree
      func_run_fasttree ALI_final.fa FastTree_ALI_final.newick
    fi

    if [ $raxML -eq 1 ]
    then
      ## If use RAxML
      echo "**** calling func_run_raxml() ****"
      func_run_raxml
    fi


	open $conf_dir_output/

	echo "All done!"

fi
