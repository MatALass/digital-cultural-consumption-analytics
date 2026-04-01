import pandas as pd
import streamlit as st


def render(filtered_df: pd.DataFrame, raw_df: pd.DataFrame, datamap_variables: pd.DataFrame, datamap_texts: pd.DataFrame):
    st.title('Methodology')

    c1, c2, c3, c4 = st.columns(4)
    c1.metric('Filtered rows', f'{len(filtered_df):,}')
    c2.metric('Raw rows', f'{len(raw_df):,}')
    c3.metric('Datamap variables', f'{len(datamap_variables):,}')
    c4.metric('Datamap text labels', f'{len(datamap_texts):,}')

    tab1, tab2, tab3, tab4 = st.tabs(['Feature engineering', 'Segment logic', 'Limitations', 'Pipeline'])

    with tab1:
        engineered = pd.DataFrame(
            {
                'feature': [
                    'engagement_score',
                    'risk_behavior_score',
                    'monetization_score',
                    'raw_content_category_count',
                    'raw_device_diversity',
                    'raw_illicit_channel_count',
                    'raw_illicit_method_count',
                    'raw_stream_ripping_score',
                    'legal_value_perception_score',
                ],
                'purpose': [
                    'Composite proxy for online and cultural intensity',
                    'Composite proxy for risk-heavy behaviors',
                    'Composite proxy for payment orientation and conversion',
                    'Breadth of raw content categories answered',
                    'Breadth of raw device usage signals',
                    'Breadth of illegal-access means reported',
                    'Breadth of concrete illicit methods reported',
                    'Average stream-ripping intensity signal',
                    'Count of legal-offer advantages and motivations selected',
                ],
            }
        )
        st.dataframe(engineered, use_container_width=True)

    with tab2:
        st.write(
            '- Premium Legal Users: high-value, legal paid, low risk.\n'
            '- Hybrid Monetizers: high-value but still using illicit channels.\n'
            '- Heavy Free Users: engaged, broad consumption, but zero spending.\n'
            '- Risk-Oriented Free Users: high observed risk intensity with illicit breadth.\n'
            '- Casual Value Seekers: some spend but lower engagement depth.\n'
            '- Low Engagement Users: default residual segment.'
        )

    with tab3:
        st.warning(
            'The project uses conservative row-order alignment between the curated analytical file and the raw barometer because the shared business key is not exposed in the processed export. That is acceptable for a portfolio project, but not equivalent to a production keyed integration.'
        )
        st.info(
            'This dashboard deliberately avoids fake causal claims and avoids pretending to semantically reconstruct all 1,500+ raw variables.'
        )

    with tab4:
        pipeline = pd.DataFrame(
            {
                'step': [
                    'Load processed analytics export',
                    'Load raw barometer',
                    'Normalize core columns',
                    'Engineer curated scores',
                    'Derive raw module features',
                    'Build rule-based segments',
                    'Serve dashboard with caching',
                ],
                'detail': [
                    'Use data/processed/data.xlsx as the main business layer',
                    'Use raw survey file for broader feature extraction',
                    'Rename fields and standardize numeric inputs',
                    'Engagement, monetization, risk, family stage, value tiers',
                    'QBU1/QBU5a/QBU10*/QBU11/QBU11B/QBU12/QBOL3/QBOL4',
                    'Interpretable non-ML segmentation',
                    'Streamlit app backed by cached loaders',
                ],
            }
        )
        st.dataframe(pipeline, use_container_width=True)
