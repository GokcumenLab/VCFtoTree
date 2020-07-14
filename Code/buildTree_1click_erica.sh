#! /bin/bash
## using the vcf files and the human refernce genome
## obtain the alignment for the any region for individuals from 1000 genomes phase 3.

## Usage: ./buildTree_1click_erica.sh #1:chr #2:start #3:end #4:specieslist #5:vcfaddress #6:numberofSpecies #7:populationlist #8:raxML #9:fastTree

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


echo "The region of your interest: chr"$chr":"$start"-"$end" for 1000 Genomes "$populationlist" population(s). Have fun!"
echo $populationlist
echo $specieslist


mkdir $conf_dir_output
cd $conf_dir_output

## STEP 1
## prepare reference sequence for your chosen chromosome
# Check file exist
[[ ! -f chr$chr.fa.gz ]] &&  wget http://hgdownload.soe.ucsc.edu/goldenPath/hg19/chromosomes/chr$chr.fa.gz
[[ ! -f chr$chr.fa ]] && gunzip -c chr$chr.fa.gz > chr$chr.fa
ref=REF_chr$chr.START$start.END$end.fa
if [ ! -f $ref]; then
    samtools faidx chr$chr.fa
    samtools faidx chr$chr.fa chr$chr:$start-$end > REF_chr$chr.START$start.END$end.fa
fi


## STEP 2
##Human Condition Met



##If array contains human 1000 Genomes
## prepare 1000 genome vcf file
if [[ $specieslist == *'Human-1000Genomes'* ]]
then
    tabix -h -f http://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.chr$chr.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz $chr:$start-$end > chr$chr.START$start.END$end.vcf
    vcffile=chr$chr.START$start.END$end.vcf

    python Code/vcf2fasta_erica.py $vcffile $ref $start $end $populationlist ALI_1000HG.fa log.txt &
    wait
    echo "vcftofasta has run."
fi


##If array only contains human
if [ $specieslist -eq 'Human-1000Genomes' ]
then
	## Tree building

    ## If use FastTree
    ## If the user need to compile it:
    if [ $fastTree -eq 1 ]
    then
        gcc -DUSE_DOUBLE -O3 -finline-functions -funroll-loops -Wall -o FastTree FastTree.c -lm
        chmod +x Code/FastTree
        Code/FastTree -gtr -gamma -nt ALI_1000HG.fa > FastTree_ALI_1000HG.newick &
        wait
    fi

    if [ $raxML -eq 1 ]
    then
        ## If use RAxML
        python Code/fas2phy.py ALI_1000HG.fa ALI_final.phy
        chmod +x Code/raxmlHPC-PTHREADS-SSE3
        Code/raxmlHPC-PTHREADS-SSE3 -T 2 -n YourRegion -s ALI_final.phy -mGTRGAMMA -p 235 -N 2 &
        wait
        mv RAxML_bestTree.YourRegion RAxML_bestTree.YourRegion.newick &
        wait
    fi

	#shopt -s extglob
	#shopt -p extglob
	mkdir ../temp
	mv Code ../temp
	mv vcftotree_gui_final.py ../temp
	mv README.md ../temp

	mv * $conf_dir_output/

	mv ../temp/* .
	rmdir ../temp

	open $conf_dir_output/

##Else if other species selected
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

        python Code/
        ## building the alignment
        python Code/vcf2fasta_otheranimals.py $customizedHuman $ref $start $end $num ALI_customized_human.fa log.txt &
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

		python Code/vcf2fasta_AltaiNean_Den_rmhetero_erica.py $vcffile_altainean $ref $start $end ALI_altainean.fa Indels_Altai.txt
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

        python Code/vcf2fasta_AltaiNean_Den_rmhetero_erica.py $vcffile_vindijanean $ref $start $end ALI_vindijanean.fa Indels_Vindija.txt
    fi


    ##If denisova in array
	if [[ $specieslist == *"Denisova"* ]]
	then
		## prepare Denisovan vcf files
		tabix -h -f http://cdna.eva.mpg.de/neandertal/altai/Denisovan/DenisovaPinky.hg19_1000g.$chr.mod.vcf.gz $chr:$start-$end > Den_chr$chr.START$start.END$end.vcf

		vcffile_den=Den_chr$chr.START$start.END$end.vcf

		python Code/vcf2fasta_AltaiNean_Den_rmhetero_erica.py $vcffile_den $ref $start $end ALI_den.fa Indels_Denisova.txt
	fi

    ##If chimp in array
	if [[ $specieslist == *"Chimp"* ]]
	then
		# getting Chimpanzee(panTro4) reference, mapped to hg19
		wget http://hgdownload.soe.ucsc.edu/goldenPath/hg19/vsPanTro4/axtNet/chr$chr.hg19.panTro4.net.axt.gz
		gunzip -c chr$chr.hg19.panTro4.net.axt.gz > chr$chr.hg19.panTro4.net.axt
		python Code/Map_panTro4Ref2hg19.py chr$chr.hg19.panTro4.net.axt $chr $start $end ALI_panTro4Ref_hg19.fa
	fi

    ##If RM in array
	if [[ $specieslist == *"Rhesus-macaque"* ]]
	then
		# getting Rhesus(RheMac3) reference, mapped to hg19
		wget http://hgdownload.soe.ucsc.edu/goldenPath/hg19/vsRheMac3/axtNet/chr$chr.hg19.rheMac3.net.axt.gz
		gunzip -c chr$chr.hg19.rheMac3.net.axt.gz > chr$chr.hg19.rheMac3.net.axt
		python Code/Map_rheMac3Ref2hg19.py chr$chr.hg19.rheMac3.net.axt $chr $start $end ALI_rheMac3Ref_hg19.fa
	fi


	##May cause error if not found
	# add gaps from log.txt
	cat ALI_customized_human.fa ALI_altainean.fa ALI_vindijanean.fa ALI_den.fa ALI_panTro4Ref_hg19.fa ALI_rheMac3Ref_hg19.fa >> ALI_temp.fa
	#rm ALI_altainean.fa
	#rm ALI_vindijanean.fa
	#rm ALI_den.fa
	#rm ALI_panTro4Ref_hg19.fa
	#rm ALI_rheMac3Ref_hg19.fa
	python Code/add_gap.py ALI_temp.fa log.txt $start $end ALI_othergenomes_wgap.fa

	cat ALI_othergenomes_wgap.fa ALI_1000HG.fa >> ALI_final.fa
	rm ALI_temp.fa


    ## If use FastTree
    ## If the user need to compile it:
    if [ $fastTree -eq 1 ]
    then
        gcc -DUSE_DOUBLE -O3 -finline-functions -funroll-loops -Wall -o Code/FastTree Code/FastTree.c -lm
        chmod +x Code/FastTree
        Code/FastTree -gtr -gamma -nt ALI_final.fa > FastTree_ALI_final.newick &
        wait
    fi

    if [ $raxML -eq 1 ]
    then
        ## If use RAxML
        rm ALI_final.phy
        python Code/fas2phy.py ALI_final.fa ALI_final.phy
        chmod +x Code/raxmlHPC-PTHREADS-SSE3
        Code/raxmlHPC-PTHREADS-SSE3 -T 2 -n YourRegion -s ALI_final.phy -mGTRGAMMA -p 235 -N 2 &
        wait
        mv RAxML_bestTree.YourRegion RAxML_bestTree.YourRegion.newick &
        wait
    fi


	#shopt -s extglob
	#shopt -p extglob

	mkdir ../temp
	mv Code ../temp
	mv vcftotree_gui_final.py ../temp
	mv README.md ../temp

	mv * $conf_dir_output/

	mv ../temp/* .
	rmdir ../temp
	open $conf_dir_output/

	echo "All done, Erica is a genius."

fi
