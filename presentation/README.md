# Presentation

This directory contains the LaTeX Beamer presentation for the Causal Rationale Extraction System.

## Building the Presentation

### Prerequisites
- LaTeX distribution (TeX Live, MiKTeX, or MacTeX)
- Beamer package (usually included)

### Build Instructions

```bash
# Build PDF
make

# Or manually
pdflatex main.tex
pdflatex main.tex

# View PDF
make view

# Clean auxiliary files
make clean
```

## Presentation Structure

1. **Problem Statement**: Overview of the challenge
2. **System Architecture**: Component breakdown
3. **Methodology**: Task 1 and Task 2 approaches
4. **Evaluation**: Metrics, baselines, ablation studies
5. **Demo**: Live demonstration (to be recorded)
6. **Results & Insights**: Key findings
7. **Future Work**: Next steps
8. **Conclusion**: Summary

## Customization

- Update `\author{Team Name}` with your team name
- Add screenshots/diagrams to replace placeholder images
- Fill in quantitative results in the evaluation section
- Record demo video or prepare live demo script
- Customize color theme if desired (see Beamer themes)

## Notes

- The presentation is designed for ~15-20 minutes
- Demo section should include live or recorded demonstration
- Results sections should be filled with actual experimental results
- Architecture diagram (architecture.png) should be created separately

