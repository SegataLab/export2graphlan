# PREREQUISITES #

**export2graphlan** requires the following additional libraries:

* BIOM ver. 2.0.1 ([biom-format](http://biom-format.org))

# INSTALLATION #

**export2graphlan** is available in Bitbucket and should be obtained using [Mercurial](http://mercurial.selenic.com/) at https://bitbucket.org/francesco-asnicar/export2graphlan.

In a Unix environment you have to type:
```
#!bash

$ hg clone ssh://bitbucket.org/francesco-asnicar/export2graphlan
```
or, alternatively:
```
#!bash

$ hg clone https://bitbucket.org/francesco-asnicar/export2graphlan
```

This will download the **export2graphlan** repository locally in the ``export2graphlan`` subfolder. You then have to put this subfolder into the system path, so that you can use **export2graphlan** from anywhere in your system:
```
#!bash

$ export PATH=`pwd`/export2graphlan/:$PATH
```
Adding the above line into the bash configuration file will make the path addition permanent. For Windows or MacOS systems a similar procedure should be followed.

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