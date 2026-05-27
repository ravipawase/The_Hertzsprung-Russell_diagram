#!/usr/bin/env python3
"""
M13 Hertzsprung-Russell Diagram Generator
==========================================

This script creates an HR diagram for the M13 globular cluster using either:
  - SDSS photometric data  (g/r bands, reaches M_g ~ 10-11)
  - HST ACS photometric data via Sarajedini+2007 VizieR catalog
    (F606W/F814W bands, reaches M_V ~ 15+)

Usage:
    hr = M13HRDiagram()
    hr.run(source='hst')    # HST deep data

Requirements:
    - astroquery
    - astropy
    - numpy
    - pandas
    - matplotlib

Author: Ravindra Pawase, Manus AI and Github copilot
Date: 2026
"""

import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from astroquery.sdss import SDSS
from astroquery.vizier import Vizier

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')


class M13HRDiagram:
    """
    A class to generate and visualize an HR diagram for the M13 globular cluster.
    
    Attributes:
        cluster_name (str): Name of the cluster
        ra (float): Right ascension of cluster center in degrees
        dec (float): Declination of cluster center in degrees
        search_radius (float): Search radius in arcminutes
        data (pd.DataFrame): Retrieved SDSS data
    """
    
    def __init__(self, cluster_name="M13", ra=250.4233, dec=36.4615, search_radius=30):
        """
        Initialize the M13 HR diagram generator.
        
        Args:
            cluster_name (str): Name of the cluster (default: "M13")
            ra (float): Right ascension in degrees (default: M13 RA)
            dec (float): Declination in degrees (default: M13 Dec)
            search_radius (float): Search radius in arcminutes (default: 30)
        """
        self.cluster_name = cluster_name
        self.ra = ra
        self.dec = dec
        self.search_radius = search_radius
        self.data = None
        self.processed_data = None
        
        print(f"Initializing {cluster_name} HR Diagram Generator")
        print(f"Cluster Center: RA={ra:.4f}°, Dec={dec:.4f}°")
        print(f"Search Radius: {search_radius} arcmin\n")
    

    def query_hst_data(self):
        """
        Query deep HST ACS photometry for M13 from the Sarajedini+2007 ACS Survey
        of Globular Clusters (VizieR catalog J/AJ/133/1658).

        Uses F606W (V-band equivalent) and F814W (I-band equivalent) filters.
        Reaches M_V ~ 15+, far deeper than SDSS.

        Returns:
            pd.DataFrame: DataFrame with columns V, I, V_minus_I, M_V, ra, dec
        """
        print("=" * 70)
        print("PHASE 1: Querying HST ACS Data (Sarajedini+2007 via VizieR)")
        print("=" * 70)

        try:
            print(f"Fetching HST ACS photometry for {self.cluster_name}...")
            print("  Catalog: J/AJ/133/1658 (ACS Survey of Globular Clusters)")
            print("  Filters: F606W (V), F814W (I)")
            print("  (Connecting to VizieR servers...)")

            viz = Vizier(
                columns=['Cluster', 'Seq', 'Vmag', 'e_Vmag', 'V-I', 'e_V-I',
                         'Imag', 'e_Imag', 'qfitV', 'qfitI', 'RAJ2000', 'DEJ2000'],
                row_limit=200000
            )
            result_list = viz.query_object('NGC 6205', catalog=['J/AJ/133/1658'])

            if not result_list or len(result_list) == 0:
                print("\n⚠ No data returned from VizieR for NGC 6205.")
                self.data = None
                return None

            df = result_list[0].to_pandas()

            # Keep NGC 6205 (M13) entries only
            df = df[df['Cluster'] == 'NGC 6205'].copy()

            if len(df) == 0:
                print("\n⚠ No M13 rows found in the returned catalog.")
                self.data = None
                return None

            # Apply quality cuts: both bands must be measured
            df = df[
                df['Vmag'].notna() & df['Imag'].notna() &
                df['V-I'].notna() &
                (df['Vmag'] > 10) & (df['Vmag'] < 28) &
                (df['Imag'] > 10) & (df['Imag'] < 28) &
                (df['e_Vmag'] < 0.3) & (df['e_Imag'] < 0.3)
            ].copy()

            # Rename columns for consistency with rest of pipeline
            df = df.rename(columns={
                'Vmag':    'V',
                'Imag':    'I',
                'V-I':     'V_minus_I',
                'e_Vmag':  'err_V',
                'e_Imag':  'err_I',
                'RAJ2000': 'ra',
                'DEJ2000': 'dec',
            })

            # Mark data source so process_data knows which columns to use
            df['_source'] = 'hst'

            self.data = df
            print(f"\n✓ Query successful!")
            print(f"  Retrieved {len(df)} stars from HST ACS catalog")
            print(f"  F606W (V) range: {df['V'].min():.2f} to {df['V'].max():.2f}")

            return self.data

        except Exception as e:
            print(f"\n⚠ Error querying VizieR HST catalog: {e}")
            self.data = None
            return None


    def process_data(self):
        """
        Process the retrieved photometric data (SDSS or HST) for HR diagram creation.

        Auto-detects the data source from the '_source' column and handles
        column names accordingly:
          - SDSS: uses g, r bands  → color = g-r,  magnitude = M_g
          - HST:  uses V, I bands  → color = V-I,  magnitude = M_V
        """
        print("\n" + "=" * 70)
        print("PHASE 2: Processing Photometric Data")
        print("=" * 70)

        if self.data is None:
            print("✗ No data available for processing")
            return None

        df = self.data.copy()
        initial_count = len(df)
        print(f"Starting with {initial_count} objects")

        # Distance modulus for M13 (~7.7 kpc)
        distance_modulus = 14.4

        # ── Detect source ──────────────────────────────────────────────────
        source = 'hst' if ('_source' in df.columns and
                            df['_source'].iloc[0] == 'hst') else 'sdss'

        if source == 'hst':
            # HST path: F606W (V) and F814W (I)
            required_cols = ['V', 'V_minus_I']
            df = df.dropna(subset=required_cols)
            print(f"  After removing NaN: {len(df)} objects")

            # Color and absolute magnitude
            df['color'] = df['V_minus_I']
            df['mag']   = df['V']
            df['M_V']   = df['V'] - distance_modulus

            # Sanity color filter
            df = df[(df['color'] > -0.5) & (df['color'] < 3.5)]
            print(f"  After color filter: {len(df)} objects")

            self._color_label = 'Color (F606W - F814W)  [mag]'
            self._mag_label   = 'Absolute Magnitude $M_{F606W}$ [mag]'
            self._plot_mag_col = 'M_V'


        # Store data source tag for the plotting step
        self._data_source = source

        print(f"\n✓ Data processing complete!")
        print(f"  Final sample:    {len(df)} stars")
        print(f"  Magnitude range: {df['mag'].min():.2f} to {df['mag'].max():.2f}")
        print(f"  Color range:     {df['color'].min():.2f} to {df['color'].max():.2f}")
        abs_mag = df[self._plot_mag_col]
        print(f"  M range:         {abs_mag.min():.2f} to {abs_mag.max():.2f}")
        print(f"  Stars with M > 8:  {(abs_mag > 8).sum()}")
        print(f"  Stars with M > 10: {(abs_mag > 10).sum()}")
        print(f"  Stars with M > 12: {(abs_mag > 12).sum()}")

        self.processed_data = df
        return df
    
    def create_hr_diagram(self, output_file='m13_hr_diagram.png', figsize=(12, 8)):
        """
        Create and save the HR diagram visualization.

        Works for both SDSS (g/r) and HST (F606W/F814W) data.
        Axis labels and title update automatically based on data source.

        Args:
            output_file (str): Path to save the output image
            figsize (tuple): Figure size in inches (width, height)
        """
        print("\n" + "=" * 70)
        print("PHASE 3: Creating HR Diagram Visualization")
        print("=" * 70)

        if self.processed_data is None:
            print("✗ No processed data available for plotting")
            return

        df   = self.processed_data
        mcol = self._plot_mag_col      # 'M_g' or 'M_V'
        src  = getattr(self, '_data_source', 'sdss')
        source_label = 'Data from hubble space telescope (ACS Photometry)' if src == 'hst' \
                       else 'SDSS Photometric Data'

        fig, ax = plt.subplots(figsize=figsize)

        scatter = ax.scatter(
            df['color'],
            df[mcol],
            c=df['color'],
            cmap='RdYlBu_r',   # red→blue: cool→hot stars
            s=5 if src == 'hst' else 20,
            alpha=0.5,
            edgecolors='none',
        )

        ax.invert_yaxis() # do you know why it is inverted ?

        ax.set_xlabel(self._color_label, fontsize=14, fontweight='bold')
        ax.set_ylabel(self._mag_label,   fontsize=15, fontweight='bold')
        ax.set_title(
            f'Hertzsprung-Russell Diagram: {self.cluster_name}\n{source_label}',
            fontsize=17, fontweight='bold', pad=20
        )

        ax.grid(True, alpha=0.3, linestyle='--')

        # Indicate the magnitude scale direction after inversion
        ax.text(0.01, 0.98, 'brighter', transform=ax.transAxes,
                fontsize=11, verticalalignment='top', horizontalalignment='left',
                color='red', fontweight='bold')
        ax.text(0.01, 0.02, 'fainter', transform=ax.transAxes,
                fontsize=11, verticalalignment='bottom', horizontalalignment='left',
                color='red', fontweight='bold')
        ax.text(0.00, -0.08, 'high temperature', transform=ax.transAxes,
                fontsize=11, verticalalignment='top', horizontalalignment='left',
                color='red', fontweight='bold', clip_on=False)
        ax.text(1.00, -0.08, 'low temperature', transform=ax.transAxes,
                fontsize=11, verticalalignment='top', horizontalalignment='right',
                color='red', fontweight='bold', clip_on=False)
        ax.text(0.02, 0.06, 'dwarfs', transform=ax.transAxes,
                fontsize=11, verticalalignment='bottom', horizontalalignment='left',
                color='red', fontweight='bold')
        ax.text(0.98, 0.94, 'giants', transform=ax.transAxes,
                fontsize=11, verticalalignment='top', horizontalalignment='right',
                color='red', fontweight='bold')

        band_note = 'F606W/F814W' if src == 'hst' else 'g/r'
        stats_text = (f'N = {len(df):,} stars\n'
                      f'Bands: {band_note}\n'
                      f'Distance: ~7.7 kpc\n'
                      f'[Fe/H] ≈ -1.33 dex')
        ax.text(0.98, 0.02, stats_text, transform=ax.transAxes,
                fontsize=9, verticalalignment='bottom', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))

        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"\n✓ HR diagram saved to: {output_file}")
        plt.show()
        return fig, ax


    def run(self, output_file='m13_hr_diagram.png', source='hst'):
        """
        Execute the complete pipeline to generate the HR diagram.

        Args:
            output_file (str): Path to save the output image
            source (str): Data source to use — 'sdss' or 'hst'
                          'sdss' → SDSS SQL query  (reaches M_g ~ 10-11)
                          'hst'  → HST ACS VizieR  (reaches M_V ~ 15+)
        """
        print("\n" + "=" * 70)
        print(f"M13 HR DIAGRAM GENERATION PIPELINE  [source={source.upper()}]")
        print("=" * 70 + "\n")

        # Step 1: Query data
        if source.lower() == 'hst':
            self.query_hst_data()
        # else:
        #     self.query_sdss_data_sql()
        else:
            raise("Only HST source is implemented")

        # Step 2: Process data
        self.process_data()

        # Step 3: Create visualization
        self.create_hr_diagram(output_file=output_file)

        print("\n✓ Pipeline complete!")


def main():
    """Main entry point for the script."""

    hr_diagram = M13HRDiagram(
        cluster_name="M13 (Hercules Cluster)",
        ra=250.4233,
        dec=36.4615,
        search_radius=30
    )

    SOURCE = 'hst'   # time being only HST is implemented

    out = r'C:\Users\hp\PycharmProjects\HR_diagram\m13_hr_diagram_{}.png'.format(SOURCE)
    hr_diagram.run(output_file=out, source=SOURCE)


if __name__ == "__main__":
    main()
