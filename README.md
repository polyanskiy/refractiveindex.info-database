## Notices

> ⚠️ **Jan 18, 2026**  
> Please use the `develop` branch for contributing new data and any edits.

> ⚠️ **Jan 7, 2026**  
> The default branch was renamed from `master` to `main`.  
> Fork maintainers should update local tracking accordingly.

# Refractive Index Database

The refractiveindex.info database is an extensive collection of optical constants for a wide range of materials. The database is in the public domain. Copyright and related rights were waived by <a href="mailto:polyanskiy@refractiveindex.info">Mikhail Polyanskiy</a> through the <a href="https://creativecommons.org/publicdomain/zero/1.0/">CC0 1.0 Universal Public Domain Dedication</a>. You may copy, modify, and distribute the refractiveindex.info database, even for commercial purposes, without asking permission.

The YAML file format is used to store material information and the database structure. Many text editors have built-in syntax highlighting for YAML markup. <a href="https://code.visualstudio.com/">Visual Studio Code</a> (cross-platform) or <a href="https://notepad-plus-plus.org/">Notepad++</a> (under Windows) are recommended for viewing and editing refractiveindex.info database files.

## Web interface

https://refractiveindex.info/

## How to cite

If you use data from this database in research, publications, reports, or software, please cite the peer-reviewed data descriptor published in *Scientific Data*:

**Reference:**

> Polyanskiy, M. N. *Refractiveindex.info database of optical constants*.  
> *Scientific Data* **11**, 94 (2024).  
> https://doi.org/10.1038/s41597-023-02898-2

**BibTeX:**
```bibtex
@article{polyanskiy2024,
  title   = {Refractiveindex.info database of optical constants},
  author  = {Polyanskiy, Mikhail N.},
  journal = {Scientific Data},
  volume  = {11},
  pages   = {94},
  year    = {2024},
  doi     = {10.1038/s41597-023-02898-2}
}
```

**Optional web citation** (not preferred over the peer-reviewed article):

> M. N. Polyanskiy, Refractive index database, https://refractiveindex.info. Accessed on YYYY-MM-DD.

When appropriate, please also cite the original publications from which specific datasets were obtained; these references are listed in the corresponding data files.

## Contributing

Contributions of new data, corrections, and improvements are welcome.

### General guidelines

- Please base all contributions on the `develop` branch.
- Follow existing conventions for directory structure, file naming, and YAML formatting.
- Ensure that all numerical data are traceable to a reliable source (peer-reviewed publications, manufacturer datasheets, etc.).

### Contributing data

There are two recommended ways to contribute data:

**Option A — YAML (preferred)**  
The database uses the YAML format internally. Providing data already formatted as YAML significantly simplifies and speeds up inclusion. Existing data files in the repository can be used as templates.

**Option B — Any format**  
Send numerical data in any common format (TXT, CSV, Excel, etc.), or a reference to a publication containing suitable data, to: <polyanskiy@refractiveindex.info>

### Contributing via GitHub

1. Fork this repository.
2. Create a feature branch from `develop`.
3. Add or modify data files and/or documentation.
4. Submit a pull request targeting the `develop` branch.

## Related projects

### refractiveindex.info-scripts
Collection of Python scripts related to the refractiveindex.info database  
https://github.com/polyanskiy/refractiveindex.info-scripts

### refractiveindex
Easy Python interface to the refractiveindex.info database  
https://github.com/toftul/refractiveindex

### RefractiveIndex.jl
Julia interface to the refractiveindex.info database  
https://github.com/stillyslalom/RefractiveIndex.jl

### PyTMM
Database browser and Transfer Matrix Method implementation  
https://github.com/kitchenknif/PyTMM

### tmmnlay
Another TMM package loosely based on PyTMM  
https://github.com/ovidiopr/tmmnlay

### refractiveindex.info-sqlite
Python 3 + SQLite wrapper for the refractiveindex.info database  
https://github.com/HugoGuillen/refractiveindex.info-sqlite

### refractiveindex.info
Support for operations not possible through the web interface (e.g., finding materials with refractive index within a specified range)  
https://github.com/cinek810/refractiveindex.info (original scripts)  
https://github.com/mtarek/refractiveindex.info (fork and further development)

### PyMoosh
Python library for multilayer simulation and optimization  
https://github.com/AnMoreau/PyMoosh

### pyElli
Ellipsometry data processing package with a built-in refractive index data loader  
https://pyelli.readthedocs.io
