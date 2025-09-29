# Tendly Dashboard

A Streamlit-based dashboard for analyzing Estonian public procurement data, focusing on tender cost distribution and analytics.

## Features

- **Cost Distribution Analysis**: Interactive bar chart with 50 cost buckets showing tender distribution
- **Real-time Filtering**: Filter by cost range, procurement sector, and procedure type
- **Multiple Visualizations**: 
  - Cost distribution with logarithmic bucketing
  - Procurement sector breakdown (pie chart)
  - Procedure type analysis (bar chart)
  - Timeline analysis of tender submissions
  - Top categories by total value
- **Data Table**: Recent tenders with key information
- **Key Metrics**: Total tenders, total value, average cost, and median cost

## Database Schema

The application connects to a PostgreSQL database containing Estonian tender details with 61 columns and 48,479+ records. Key fields include:

- `estimated_cost`: Primary field for cost analysis
- `tender_name`: Tender title
- `primary_cpv_name`: Procurement category
- `procurement_sector_code`: Sector classification
- `submission_deadline`: Timeline information

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Update the `DB_URL` variable with your database connection string
   - For Streamlit Cloud deployment, add `DB_URL` as a secret in your app settings

3. Run the application:
```bash
streamlit run Home.py
```

4. Open your browser to `http://localhost:8501`

## Database Connection

The application uses SQLAlchemy to connect to the PostgreSQL database via the `DB_URL` environment variable:
- Format: `postgresql://username:password@host:port/database`
- Table: `estonian_tender_details`
- Uses connection pooling and caching for optimal performance

## Cost Bucketing Strategy

The dashboard uses logarithmic bucketing for the cost distribution to handle the wide range of tender values effectively:

- 50 buckets distributed on a logarithmic scale
- Automatic formatting (€1K, €1M, etc.)
- Handles values from hundreds to millions of euros
- Filters out NULL and zero values

## File Structure

```
tendly-dashboard/
├── Home.py                 # Main Streamlit application
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── db/
│   ├── schema.json        # Database schema export
│   └── extract_schema.py  # Schema extraction script
└── analysis/
    └── estonian_tender_details_analysis.md  # Data analysis notes
```

## Usage

1. **Filters**: Use the sidebar to filter data by cost range, sector, and procedure type
2. **Cost Distribution**: Main chart shows tender count distribution across 50 cost buckets
3. **Sector Analysis**: Pie chart breakdown by procurement sector
4. **Timeline**: Line chart showing tender submissions over time
5. **Categories**: Top 10 categories by total estimated value
6. **Data Table**: Browse recent tenders with key details

## Data Caching

The application uses Streamlit's caching mechanisms:
- Database connection caching (`@st.cache_resource`)
- Data loading caching with 10-minute TTL (`@st.cache_data`)

## License

This project is licensed under the MIT License - see the LICENSE file for details.