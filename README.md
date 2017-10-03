**INSTALLATIONS AND INSTRUCTIONS ARE UNDER V1.0.0, PLEASE READ THEM VERY CAREFULLY!**

**PLEASE MAKE SURE YOU HAVE INSTALLED ALL THE NECESSARY TOOLS AS DESCRIBED BEFORE USING THE VCFTOTREE**

# VCFtoTree v3.0.0
Updates:
- It can now be applied to other species besides human.
- In human section, you can also add in your customized vcf files, and you can specify the number of individuals in your vcf file.
- Users can choose whether to build the tree or not, also to build the tree using either [FastTree] or RAxML. (To note that, VCFtoTree v3.0.0 compiles the FastTree with ```-DUSE_DOUBLE``` by default, lifting the hard-coded limit on branch length precision. Please see detail in this [blog].)
- **!!!!!!!!!Vindija Neanderthal can NOT be used!!!!!!!!!** in this version right now due to the fact that the data haven't been published. It will be updated once it is published.

- To use the functioal of "other species" and "customized human", if your customized vcf file or reference are from a local address, please enter the full address of the file.
- For customized vcf file and reference file, please use the compressed version of them as in "***.fa.gz" or "***.vcf.gz", the program will index them for you.
- To enter the URL of your customized file, please use the URL begins with "http://".


[FastTree]:http://www.microbesonline.org/fasttree/
[blog]:http://darlinglab.org/blog/2015/03/23/not-so-fast-fasttree.html

#### APP download site:
https://www.dropbox.com/sh/sewjxmh9207fp89/AAASfUGqMBtd2_HO3CR7XA3ha?dl=0

**INSTALLATIONS AND INSTRUCTIONS ARE UNDER V1.0.0, PLEASE READ THEM VERY CAREFULLY!**

**PLEASE MAKE SURE YOU HAVE INSTALLED ALL THE NECESSARY TOOLS AS DESCRIBED BEFORE USING THE VCFTOTREE**

# VCFtoTree v2.0.0
Updates:
- Now users can choose the populations that they are interested, or "ALL" to include all the populations.
- Added the new Neanderthal [Vindija] to the GUI. 

[Vindija]:http://cdna.eva.mpg.de/neandertal/Vindija/VCF/Vindija33.19/

#### APP download site:
https://www.dropbox.com/sh/sewjxmh9207fp89/AAASfUGqMBtd2_HO3CR7XA3ha?dl=0




# VCFtoTree v1.0.0
Build phylogeny from [1000 Genomes] Phase 3 VCF file for 2504 individuals, also including ancient ([Neanderthal], [Denisovan]) and primate genomes.

[1000 Genomes]:http://www.1000genomes.org
[Neanderthal]:http://www.eva.mpg.de/neandertal/index.html
[Denisovan]:http://www.eva.mpg.de/denisova/index.html

VCF --> fasta sequence (whole sequence, not just variable sites) --> Phylogeny

We provide a user friendly interface, in which you can choose the genomes you want to add into the phylogeny.

Raw scripts can be found in **Code** folder.

#### Availability and requirement
VCFtoTree was designed for Mac OS users, has been tested on El Captian V10.11.5 with python 2.7.11

Here are the programs/packages needed to run the VCFtoTree.
- For first time users, you need to make sure your Mac has install the [command line tools] from Apple.com
- [samtools] executable file needs to be installed in your /usr/local/bin
- [tabix] needs to be installed in your /usr/local/bin
- [wget] needs to be installed in your /usr/local/bin
- [gcc] needs to be installed in your /usr/bin

[samtools]:http://www.htslib.org
[tabix]:https://github.com/samtools/tabix
[wget]:https://developer.apple.com/opensource/
[command line tools]:https://developer.apple.com/opensource/
[gcc]:https://gcc.gnu.org/

The easiest way to check if you have those tools, type the commands below into your Terminal:

```unix
find /usr/local/bin/tabix

find /usr/local/bin/samtools

find /usr/local/bin/wget

find /usr/bin/gcc
```
After making sure that you have the above three tools installed, you can download and use the app now.

The running time of the app mostly depends on 1) downloading the Neanderthal vcf file; 2) building the phylogeny using RAxML.

After the whole process finishing, the app will generate a **VCFtoTree_Output** folder right next to your application in which you can find the newick tree file and all other output files.

**The folder will be empty before the app finishes, after the app finished, the folder will be open automatically, you will be able to see all the files generated. After each run, please change the previous output folder name to something else to avoid overwrite.**

On the screen there will also be message saying that "Your tree is completed."

Your tree file is the file with **".newick"** extention.

#### APP download site:
https://www.dropbox.com/sh/sewjxmh9207fp89/AAASfUGqMBtd2_HO3CR7XA3ha?dl=0

#### 1.0.0
The first working version of VCFtoTree.app.


