# PREREQUISITES #
You need to have export2graphlan.py and GraPhlAn installed and exported in you Bash PATH variable.
export2graphlan.py requires the following additional packages:

* BIOM ver. 2.0.1 ([biom-format](http://biom-format.org))

# INSTALLATION #

TBA

# USAGE #
TBA

# EXAMPLES #
There are an *examples* folder that contains the following examples: *hmp_aerobiosis*.
Examples should work just by typing in a terminal shell (provided that you are inside one of the example folder) the following command:

```
#!bash

$ ./PIPELINE.sh
```

If everything goes well you should find in the same folder of the example six new files: *annot.txt*, *outimg.png*, *outimg_annot.png*, *outimg_legend.png*, *outtree.txt*, and *tree.txt*. Where:

* *annot.txt*: contains the annotation that will be used by GraPhlAn, produced by the export2graphlan.py script
* *outimg.png*: is the circular tree produced by GraPhlAn
***outimg_annot.png*: contains the annotation legend of the circular tree
* *outimg_legend.png*: contains the legends of the highlighted biomarkers in the circular tree
* *outtree.txt*: is the annotated tree produced by graphlan_annotate.py
* *tree.txt*: is the tree produced by the export2graphlan.py script

# CONTACTS #
Francesco Asnicar (francescoasnicar@gmail.com)