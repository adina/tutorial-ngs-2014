=================================================
So you want to start using that big data in NCBI?
=================================================

===================
Learning objectives
===================
This is a tutorials for working with the data that is available in NCBI.  The learning objectives for this tutorial are as follows:

1.  To be able to download specific gene sequences or genomes from NCBI (even with a big list of gene sequences).
2.  To be able to create use these genes as a database to annotate a sequencing dataset.
3.  To estimate the number of genes and their corresponding annotations in multiple sequencing datasets.

You will need to know some things prior to this tutorial:

1.  Familiarity with the structure of NCBI website and their nucleotide and genome databases.
2.  Ability to navigate in the unix shell.
3.  Ability to execute programs in the shell.
4.  Access and login to an Amazon EC2 instance or similar ubuntu-based server

The key challenge that we will work through...or your mission, if you choose to accept it, is to identify nitrogen fixation genes found in sequencing DNA from soils.

You have been delivered three dogma-changing metagenomes (sequencing datasets) originating from three different Iowa crop soils (corn, soybean, and prairie).  You are interesting in identifying nitrogen fixation genes that are associated with native bacteria in these soils.  Nitrogen fixation is a natural process performed by bacteria that converts nitrogen in the atmosphere into a form that is usable for plants.  If we can optimize natural nitrogen fixation, our hope is to reduce nitrogen fertilizer inputs that may contribute to the eutrophication of downstream waters (e.g., dead zones in the Gulf of Mexico).

==========
Your tools
==========

Get your EC2 instance going - you need an Ubuntu 14.0 based instance (64-bit) with at least 4 cores.
Then install the software::

    sudo bash
    apt-get update

Then...::

    cd /root
    apt-get -y install gcc git screen curl make python-pip

And finally...::

    pip install screed
    curl -O ftp://ftp.ncbi.nih.gov/blast/executables/release/2.2.26/blast-2.2.26-x64-linux.tar.gz
    tar xzf blast-2.2.26-x64-linux.tar.gz
    cp blast-2.2.26/bin/* /usr/local/bin
    cd /home/ubuntu

================
Getting the Data
================

Task 1
------
Get the metagenome datasets and scripts related to this tutorial.

All the tutorial materials are contained on a Github repository.  The reason for using Github is that this material can be updated by me and grabbed by you lucky folk seamlessly with just a couple commands.  If you are interested in learning more about Git, see these [tutorials]()::

    git clone https://github.com/adina/bodega-howe-ncbi.git

This command will make a directory (or folder for those more Finder/Explorer inclined) named "bodega-howe-ncbi" in the location where it was run.  Within that directory, there will be two directories containing "data" and "scripts".  You can see this by navigating (hint:  cd) to the "bodega-howe-ncbi" directory and typing::

    ls -lah

Task 2
------
Navigate to the data directory and identify the number of sequences in each file.  Hint:  To find specific characters in a file, you can use [grep](http://www.gnu.org/software/grep/manual/html_node/Usage.html).  For example, to find all instances of AGTC in the corn.fa file, we could::

    grep AGTC corn.fa

To find sequences, we know that each sequence will start with a special character, ">".  This character in the shell, remember, is a bit special.  So to find it as a symbol in the text, we're going to put a '^' right before it in quotes::

    grep ^">" corn.fa

Now, to count, you'll remember we can use the command "wc", with a pipe...So you're command will look something like this::

    grep ^">" corn.fa | wc

Or...if you want to do this quicky::

    for x in *fa; do echo $x; grep ^">" $x | wc; done

To identify nitrogen fixation genes, you've been tasked to build a database of all previously observed known nitrogen fixation genes (nifH).  To build this database, you have been reading literature for about two weeks and come up with a list of about 30 genes:

gi|985477984|emb|LN997366.1|

gi|985477986|emb|LN997367.1|

gi|985477988|emb|LN997368.1|

gi|985477990|emb|LN997369.1|

...

gi|38679|emb|X51500.1|

gi|470075|emb|Z31716.1|

You'll also see this list in a file in the data directory (hint:  use cat).

Task 3
------
Check out the file containing these gene IDs.

You have a sinking feeling like this isn't really leveraging the big data biology that everyone says sequencing technologies have provided.  You've decided to check out NCBI for its contents.

Task 4
------
Go to the NCBI webpage and identify an estimate of total nifH genes and download a list of their accession numbers.

You'll want to navigate in a web-browser to the http://www.ncbi.nlm.nih.gov/.  You'll see in the search query box that you can search a number of databases.  Here, we want to look at the nucleotide database and query something along the lines of nifH or nitrogen fixation.

When I did this, there were nearly 180,000 genes that were hit by this query.  You will want to look for the "Send To" link at the upper right of the page (put on a magnifying glass!), and download the GI list for this query.

Task 5
------
Find that file on your computer and give it a peek.  If you're feeling up for it, transfer it to your EC2 instance (hint:  scp).

To make this tutorial not-as-painful to complete in a reasonable amount of time, I've also made a list of 300 nifH genes from NCBI and put them in a file '300-nifh-genes.txt' in the data directory.  I would highly suggest you use this gene to build your database going forward in this tutorial.

Task 6
------
Take a look at this file.  Prove to yourself that it contains 300 genes (Hint:  wc)

.. Note::

    Some of these hits, I am sure, are likely not nifH.  Typically, I would do some clean up of these genes to filter out any annotation that did not contain "nifH".  In case you're interested, this script is in the scripts directory and is called "clean-up.py".  You are welcome to play with it.  Here's the command:  python clean-up.py <fasta-file-uncleaned> > <fasta-file-cleaned>


Now, we are going to learn how to download these genes (by learning about the NCBI API below)

Task 7
------
Think about how you would download this data if you didn't have this tutorial.

You may have thought about some of the following:

#. Go to the web portal and look up each FASTA
#. Go to the `FTP site <ftp://ftp.ncbi.nlm.nih.gov/refseq/>`_, find each genome, and download manually
#. Use the NCBI Web Services API to download the data

Among these, I'm going to assume many of you are familiar with the first two.  This tutorial then is going to focus on using APIs.

================================
Scaling "Getting the Data" On Up
================================

Here's some `answers <http://stackoverflow.com/questions/7440379/what-exactly-is-the-meaning-of-an-api>`_, among which my favorite is "an interface through which you access someone else's code or through which someone else's code accesses yours -- in effect the public methods and properties."

The NCBI has a whole toolkit which they call *Entrez Programming Utilities* or *eutils* for short.  You can read all about it in the `documentation <http://www.ncbi.nlm.nih.gov/books/NBK25501/>`_.  There are a lot of things you can do to interface with all things NCBI, including publications, etc., but I am going to focus today on downloading sequencing data.

To do this, you're going to be using one tool in *eutils*, called *efetch*.  There is a whole chapter devoted to `efetch <http://www.ncbi.nlm.nih.gov/books/NBK25499/#chapter4.EFetch>`_ -- when I first started doing this kind of work, this documentation always broke my heart.  Its easier for me to just show you how to use it.

Task 8
------

Open a web browser, and check out what NCBI knows about this gene.  Check it out `here <http://www.ncbi.nlm.nih.gov/nuccore/X51500.1>`_.

Task 9
------

Download the gene with eutils commands in your web-browser and take a look at the file.

On your web-browser, paste the following URL to download the nucleotide genome for gene X51500.1::

    http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=X51500.1&rettype=fasta&retmode=text

Task 10
-------

Try downloading the GenBank file instead by pasting this onto your web-browser::

   http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=CP000962&rettype=gb&retmode=text

Do you notice the difference in these two commands?  Let's breakdown the command here:

#.  <http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?>  This is command telling your computer program (or your browser) to talk to the NCBI API tool efetch.
#.  <db=nuccore>  This command tells the NCBI API that you'd like it to look in this particular database for some data.  Other databases that the NCBI has available can be found `here <http://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi>`_.
#.  <id=X51500.1>  This command tells the NCBI API efetch the ID of the gene/genome you want to find.
#.  <rettype=gb&retmode=text>  These two commands tells the NCBI how the data is returned.  You'll note that in the two examples above this command varied slightly.  In the first, we asked for only the FASTA sequence, while in the second, we asked for the Genbank file.  Here's some elusive documentation on where to find these `"return" objects <http://www.ncbi.nlm.nih.gov/books/NBK25499/table/chapter4.T._valid_values_of__retmode_and/?report=objectonly>`_.

Also, a useful command is also <version=1>.  There are different versions of sequences and some times that is useful.  For reproducibility, I try to specify versions in my queries, see these `comments <http://www.ncbi.nlm.nih.gov/Class/MLACourse/Modules/Format/exercises/qa_accession_vs_gi.html>`_.

.. Note::

   Notice the "&" that comes between each of these little commands, it is necessary and important.


Ok, let's think of automating this sort of query.  So...we're moving from your lil laptop to your jumbo EC2 instance now.

Task 11
-------
Download a gene sequence on the command line.

Going back onto your instance, in the shell, you could run the same commands above with the addition of *curl* on your EC2 instance::

    curl "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=X51500.1&rettype=fasta&retmode=text"

You'll see it fly on to your screen.  Don't panic - you can save it to a file and make it more useful BUT note the path you are in and where you will save this file (as long as you know...that's fine)::

    curl "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=X51500.1&rettype=fasta&retmode=text" > X51500.1.fa

You could now imagine writing a program where you made a list of IDs you want to download and put it in a for loop, *curling* each genome and saving it to a file.  The following is a `script <https://github.com/adina/tutorial-ngs-2014/blob/master/ncbi/fetch-genomes.py>`_.  Thanks to Jordan Fish who gave me the original version of this script before I even knew how and made it easy to use.

To see the documentation for this script in the scripts directory::

    python fetch-genomes-fasta.py

You'll see that you need to provide a list of IDs and a directory where you want to save the downloaded files.

Task 12a
--------

Run this script (note that your paths for the script or data may need to be specified) -- also see note below::

    python scripts/fetch-genomes-fasta.py data/300-nifh-genes.txt data/nifh-database-fastas

Sit back and think of the glory that is happening on your screen right now...

.. Note::

    If you are nervous....you may want to run this on just a few of these IDs to begin with.  You can create a smaller list using the *head* command with the -n parameter in the shell.  For example, head -n 3 300-nifh-genes.txt > 3genes.txt.

Task 12b
--------
After all the 300 genes are downloaded, you will want to concatenate them into one file (Hint cat and >>), named "all-nifH.fa".

Task 13
-------
Look at the script/program content in "fetch-genomes-fasta.py".

The meat of this script uses the following code::

    url_template = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nucleotide&id=%s&rettype=gb&retmode=text"

You'll see that the *id* here is a string character which is obtained from list of IDs contained in a separate file.  The rest of the script manages where the files are being placed and what they are named.  It also prints some output to the screen so you know its running.

Task 14
-------
Take a break.   Put up your pink stickie if you need help with this.

====================================
Comparing your data to the databases
====================================

So there are lots of ways to do this and arguably "blasting" is one of the most common.  If you're already familiar with how to run BLAST, you can just tackle this next task.  Else, instructions from Titus Brown's NGS course are below.

Task 15
-------
Format your nifH database for BLAST and then perform an alignment (with BLAST) of your metagenomes against your new database.  You should also add your lit search genes (those 30 genes) into your NCBI downloaded genes if you're up to the challenge -- it takes a couple steps.  I would suggest something like the following variables::

    blastall -i <metagenome file> -d <nifh-db> -m 8 -a 8 -p blastn -o <metag.blastnout.m8> -b 1 -e 1e-5

This takes a bit of time...so stretch a bit.  Like all good bioformaticians, you should go do something fun while the computer does all the work.  If you want to see it running, try using the "top" command.

.. Note::

    `BLAST initiation or refresher tutorial <http://angus.readthedocs.org/en/2014/running-command-line-blast.html>`_.  I have put a cheatsheet of the commands I used in the scripts directory -- if you need another hint.

Task 16
-------
Examine your blast outputs.  What do the first few lines contain?  How many hits do you have per metagenome to your database?

=======================
Next steps, what's next
=======================

Let's step back.  What is the reason for annotating your genes?  You want to get an idea of what genes are in each soil metagenome as well as a quantitative estimate of each gene.   Eventually, you would likely use this information to do some statistical analyses -- maybe in sophisticated packages like Qiime, Mothur, or Phyloseq.  All these programs take similar inputs, and the big secret is knowing what they are and how to parse/move/shift/wrangel this information into the specific format needed for each program:

#. Metadata/Environmental data - What treatment does corn.fa represent -- duh, corn!  When was it sampled?  What kind of other data have you collected on this sample (amount of fertilizer, etc).
#. Annotation information - What are the corresponding annotations to whatever shortcut ID associated with your genes (e.g., GI number).  This file can also contain some ontology / hierarchical information (e.g., Taxonomy domains / phyla / species).
#. Abundance estimates - What are the estimates of each gene in each metagenome sample.

Of these, you should be able to make a metadata file for your experiment.  The annotation file can be provided by your database.

You have a list of genes GI IDs and can pull the annotation of the gene from the header in the database nucleotide file OR better yet from the Genbank file.  For example, you might pull out the lineage of each gene from the Genbank file and have taxonomy to provide for each gene.

Perhaps the most difficult is to get the abundance estimates.  Intuitively, you can think about how to get this out of the BLAST outputs.  I observed Gene X, Y times in dataset I, Z times in dataset II.  Fortunately, I have a script to do this computationally.

Task 17
-------
Produce an abundance table of all genes in your 3 metagenomes::

    python count-up.py <all your blast output files>

For example::

    python scripts/count-up.py  data/*blastnout

This script produces a file, 'summary-count.tsv'.

Task 18
-------
Take a look at 'summary-count.tsv'.  What's in it?

Task 19
-------
Often, I get really excited and need to know what gene is associated with each Gene ID.  I like to pull in my annotations.  Let's add the annotations by giving this a try::

    python import-ann.py <blast database fasta file> summary-count.tsv > <output file>

For example::

    python import-ann.py nif-genes.fa summary-count.tsv > summary-count-annotated.tsv

Task 20
-------
Transfer the annotated file over to your laptop and open it in Excel.

==========
Conclusion
==========

You now have the foundation for having some sequencing data that you need to compare to any database.  You should be able to generate the information needed to perform statistical analyses.  Note, that you can do this for specific genes and also genomes...!    Now, go forth and conquer!


====================================================
Bonus Material on Genbank Files and Genome downloads
====================================================

Try modifying the fetch-genomes-fasta.py script to download just the Genbank file of the genes.

Some comments on Genbank files:

Download a bacterial genome's genbank file.

Genbank files have a special structure to them.  You can look at it and figure it out for the most part, or read about it in detail `here <http://www.ncbi.nlm.nih.gov/Sitemap/samplerecord.html>`_.  To find out if your downloaded Genbank files contain 16S rRNA genes, I like to run the following command::

    grep 16S *gbk

This should look somewhat familiar from your shell lesson, but basically we're looking for anylines that contain the character "16S" in any Genbank file we've downloaded.  Note that you'll have to run this in the directory where you downloaded these files.

The structure of the Genbank file allows you to identify 16S genes.  For example, ::

         rRNA        9258..10759
                     /gene="rrs"
                     /locus_tag="CLK_3816"
                     /product="16S ribosomal RNA"
                     /db_xref="Pathema:CLK_3816"

You could write code to find text like 'rRNA' and '/product="16S ribosomal RNA"', grab the location of the gene, and then go to the FASTA file and grab these sequences.  I've done that before.

You could also use existing packages to parse Genbank files.  I have the most experience with BioPython.  To begin with, let's just use BioPython so you can get to using existing scripts without writing scripts.


First, we'll have to install BioPython on your instance and they've made that pretty easy::

    apt-get install python-biopython

Fan Yang (Iowa State University) and I wrote a script to extract 16S rRNA sequences from Genbank files, `here <https://github.com/adina/tutorial-ngs-2014/blob/master/ncbi/parse-genbank.py>`_.  It basically searches for text strings in the Genbank structure that is appropriate for these particular genes.  You can read more about BioPython `here <http://biopython.org/DIST/docs/tutorial/Tutorial.html>`_ and its Genbank parser `here <http://biopython.org/DIST/docs/api/Bio.GenBank-module.html>`_.

To run this script on the Genbank file for CP000962::

    /usr/bin/python parse-genbank.py genbank-files/CP000962.gbk > genbank-files/CP000962.gbk.16S.fa

The resulting output file contains all 16S rRNA genes from the given Genbank file.

To run this for multiple files, I use a shell for loop::

    for x in genbank-files/*; do /usr/bin/python parse-genbank.py $x > $x.16S.fa; done

There are multiple ways to get this done -- but this is how I like to do it.

And there you have it, you can now pretty much automatically grab 16S rRNA genes from any number of genomes in NCBI databases.
