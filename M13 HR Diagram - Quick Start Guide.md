# M13 HR Diagram - Quick Start Guide

## Installation (5 minutes)

### 1. Install Required Packages

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install astroquery astropy numpy pandas matplotlib
```

### 2. Verify Installation

```bash
python3 -c "import astroquery; print('✓ astroquery installed')"
```

## Running the Script (1-2 minutes)

### Basic Usage

```bash
python3 m13_hr_diagram.py
```

This will:
- Query SDSS for M13 photometric data (or use simulated data if unavailable)
- Process the data
- Generate an HR diagram
- Save as `m13_hr_diagram.png`

### Output

You'll see progress output like:

```
Initializing M13 (Hercules Cluster) HR Diagram Generator
Cluster Center: RA=250.4233°, Dec=36.4615°
Search Radius: 30 arcmin

======================================================================
M13 HR DIAGRAM GENERATION PIPELINE
======================================================================

======================================================================
PHASE 1: Querying SDSS Database
======================================================================
...
✓ Query successful!
  Retrieved 500 stars from SDSS
...
✓ HR diagram saved to: m13_hr_diagram.png
```

## Understanding the Output

### The HR Diagram

The generated image shows:

- **X-axis**: Color (g - r) in magnitudes
  - Left (blue): Hotter, younger stars
  - Right (red): Cooler, older stars

- **Y-axis**: Absolute Magnitude (M_g)
  - Top (negative): Brighter, more luminous stars
  - Bottom (positive): Fainter, less luminous stars

### Key Features

1. **Main Sequence** (diagonal band, lower right)
   - Most stars in this region
   - Hydrogen-burning stars
   - Color range: 0.3-0.8 mag

2. **Red Giant Branch** (vertical sequence, upper left)
   - Evolved stars
   - Helium-burning or exhausted hydrogen
   - Color range: 0.8-1.2 mag

3. **Horizontal Branch** (horizontal sequence, middle)
   - Helium-burning stars
   - Less prominent in M13

## Customization

### Change Output Filename

Edit `m13_hr_diagram.py` and modify the last line:

```python
if __name__ == "__main__":
    hr_diagram = M13HRDiagram()
    hr_diagram.run(output_file='my_custom_name.png')
```

### Query a Different Cluster

```python
hr_diagram = M13HRDiagram(
    cluster_name="M92",
    ra=259.2833,
    dec=43.1362,
    search_radius=30
)
hr_diagram.run()
```

### Use Programmatically

```python
from m13_hr_diagram import M13HRDiagram

# Create instance
hr = M13HRDiagram()

# Run pipeline
hr.run()

# Access processed data
print(f"Number of stars: {len(hr.processed_data)}")
print(hr.processed_data.head())

# Create custom plot
import matplotlib.pyplot as plt
plt.scatter(hr.processed_data['g_minus_r'], 
            hr.processed_data['M_g'])
plt.show()
```

## Troubleshooting

### Issue: "ModuleNotFoundError"

**Solution**: Install missing packages:
```bash
pip install astroquery astropy numpy pandas matplotlib
```

### Issue: Script runs slowly

**Solution**: This is normal for the first run. Subsequent runs may be faster if data is cached.

### Issue: No data retrieved from SDSS

**Solution**: The script automatically falls back to simulated data. This is fine for demonstration. For real SDSS data, ensure you have internet access.

### Issue: Image not created

**Solution**: Check that you have write permissions in the current directory:
```bash
ls -la .
```

## Data Sources

- **SDSS Data Release**: DR19 (July 2025)
- **Cluster Coordinates**: M13 center at RA=250.4233°, Dec=36.4615°
- **Distance Modulus**: 14.4 (m - M for M13)
- **Cluster Properties**:
  - Distance: ~7.7 kpc
  - Metallicity: [Fe/H] ≈ -1.33 dex
  - Age: ~13 billion years

## Next Steps

### Explore the Code

1. Open `m13_hr_diagram.py` in a text editor
2. Read the comments and docstrings
3. Understand each phase of the pipeline

### Modify and Experiment

1. Change the distance modulus to see how it affects the diagram
2. Add extinction corrections
3. Filter for specific magnitude ranges
4. Create diagrams for multiple clusters

### Advanced Features

1. Cross-match with Gaia for accurate parallax distances
2. Overlay theoretical isochrones
3. Estimate stellar ages
4. Calculate mass functions

## References

- SDSS Documentation: https://www.sdss.org/
- Astroquery: https://astroquery.readthedocs.io/
- M13 Properties: https://en.wikipedia.org/wiki/Messier_13

## Support

For issues or questions:

1. Check the main README.md
2. Review the inline comments in the script
3. Consult the SDSS and astroquery documentation

## Tips

✓ **Pro Tips**:
- Run the script multiple times to see different random simulations
- Modify the `np.random.seed()` value to generate different data
- Increase `n_stars` in `generate_simulated_data()` for more stars
- Use `figsize=(16, 10)` for larger plots
- Save plots as PDF for publications: `output_file='diagram.pdf'`

---

**Happy exploring!** 🌟
