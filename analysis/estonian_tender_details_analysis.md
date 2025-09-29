# Estonian Tender Details Analysis

## Table Overview
- **Table Name**: `estonian_tender_details`
- **Total Rows**: 48,479 records
- **Total Columns**: 61 columns

## Key Cost-Related Fields

### Primary Cost Field
- **`estimated_cost`**: Double precision field containing the estimated cost of tenders
  - Data type: `double precision`
  - Contains values like: 20000.0, 88000.0, 100000.0, 300000.0
  - This will be the primary field for cost bucketing analysis

### Cost-Related Boolean Fields
- **`is_cost_classified`**: Boolean indicating if cost information is classified
- **`show_cost`**: Boolean indicating if cost should be displayed

## Important Categorical Fields for Analysis

### Procurement Information
- **`procurement_id`**: Unique identifier for each procurement
- **`tender_name`**: Name/title of the tender
- **`short_description`**: Brief description of the procurement
- **`procedure_type_code`**: Type of procurement procedure (LM, T, A, etc.)
- **`procurement_type_code`**: Category of procurement
- **`procurement_sector_code`**: Sector classification

### Geographic Information
- **`nuts_code`**: NUTS (Nomenclature of Territorial Units for Statistics) code
- **`location_additional_info`**: Additional location details

### Temporal Information
- **`submission_deadline`**: When submissions are due
- **`submission_opening_date`**: When submissions are opened
- **`publication_date`**: When the tender was published
- **`contract_start_date`**: When the contract begins
- **`duration_in_months`**: Contract duration

### Classification
- **`primary_cpv_code`**: Common Procurement Vocabulary code
- **`primary_cpv_name`**: Description of the CPV category

## Sample Data Insights

From the sample data, we can see:

1. **Cost Range**: Estimated costs range from €20,000 to €300,000+ in the sample
2. **Procurement Types**: Various types including vehicle purchases, software development, medical equipment, transport services
3. **Geographic Coverage**: Primarily Estonia (EE) with specific regional breakdowns
4. **Sectors**: Mix of public sector procurements (K = Public sector)

## Dashboard Requirements

### Cost Bucketing Strategy
- Create 50 buckets for the `estimated_cost` field
- Handle NULL values appropriately
- Consider logarithmic or linear bucketing based on data distribution
- Filter out classified costs if needed (`is_cost_classified = False`)

### Recommended Visualizations
1. **Primary**: Bar chart with 50 cost buckets showing tender count distribution
2. **Secondary**: 
   - Pie chart by procurement sector
   - Timeline of tender submissions
   - Geographic distribution
   - Top CPV categories by cost

### Data Quality Considerations
- Some records have NULL `estimated_cost` values
- Some costs are classified (`is_cost_classified = True`)
- Need to handle currency consistently (appears to be EUR)
