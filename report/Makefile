.PHONY: all clean view

all: main.pdf

main.pdf: main.tex
	pdflatex main.tex
	pdflatex main.tex

clean:
	rm -f *.aux *.log *.out *.toc *.bbl *.blg

view: main.pdf
	xdg-open main.pdf 2>/dev/null || open main.pdf 2>/dev/null || echo "Please open main.pdf manually"

