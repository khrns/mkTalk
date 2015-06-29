.PHONY: all clean

MAIN = ${rootname}

all:
	pdflatex ${MAIN}
	pdflatex ${MAIN}

clean:
	rm -f ${MAIN}.toc
	rm -f ${MAIN}.aux
	rm -f slides/*/*.aux
	rm -f ${MAIN}.log
	rm -f ${MAIN}.pdf
	rm -f ${MAIN}.out
	rm -f ${MAIN}.nav
	rm -f ${MAIN}.snm
