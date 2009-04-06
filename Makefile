all: doc

doc: doc_man doc_html

doc_html: html-stamp

html-stamp: date2name.1.txt
	asciidoc -b xhtml11 -a icons date2name.1.txt
	touch html-stamp

doc_man: man-stamp

man-stamp: date2name.1.txt
	asciidoc -d manpage -b docbook date2name.1.txt
	sed -i 's/<emphasis role="strong">/<emphasis role="bold">/' date2name.1.xml
	xsltproc /usr/share/xml/docbook/stylesheet/nwalsh/manpages/docbook.xsl date2name.1.xml
	# ugly hack to avoid duplicate empty lines in manpage
	# notice: docbook-xsl 1.71.0.dfsg.1-1 is broken! make sure you use 1.68.1.dfsg.1-0.2!
	cp date2name.1 date2name.1.tmp
	uniq date2name.1.tmp > date2name.1
	# ugly hack to avoid '.sp' at the end of a sentence or paragraph:
	sed -i 's/\.sp//' date2name.1
	rm date2name.1.tmp
	touch man-stamp

clean:
	rm -rf date2name.1.html date2name.1.xml date2name.1.html-stamp man-stamp html-stamp

codecheck:
	pylint --include-ids=y --max-line-length=120 date2name

# graph:
#	pycallgraph date2name -s *
