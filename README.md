# VCFtoTree 


# Requirements

Before running the program please make sure that the following software packages are installed.

* Make sure you have python 3 installed [Python]:https://www.python.org/downloads/
* Install [Tabix]:https://github.com/samtools/tabix tools
* Install [samtools]:http://www.htslib.org/
* If you want to use Fast Tree, Install [FastTree]:http://www.microbesonline.org/fasttree/
  * Install [gcc]:https://gcc.gnu.org/ for compiling fasttree



# Running
Download the repository and make sure that you installed all the required libraries.

Before running the program edit `vtt.config` file and change `conf_dir_output` folder location. The produced output files will be placed in this location.

To run the Graphical User Interface, just type the following command inside the downloaded repository folder.

```python3  vcftotree_gui.py```

For detailed instructions you can also browse VCFtoTreeManual.pdf.
