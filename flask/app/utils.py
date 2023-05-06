import base64
from io import BytesIO

import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

def parse_result(res):
    res_df = pd.DataFrame(res)

    res_by_metric = res_df.groupby('elem_id').agg(list).reset_index()

    # elem_id to prompts / completions
    prompt_completions_dict = {row.elem_id: (row.prompt[0], row.completion) for row in res_by_metric.itertuples()}

    metric_values = {}

    for disp_name, metric, fig_xlabel in [('Elapsed Time', 'elapsed_time', 'Elapsed time (s)'), \
                                          ('Number of characters', 'num_chars', '# characters'), \
                                          ('Number of tokens', 'num_tokens', '# tokens')]:
        tmp = {}
        # figure
        b64_str = get_b64_boxplot(res_by_metric, metric, fig_xlabel)
        tmp['fig'] = b64_str

        # table
        tmp['tab'] = get_table_components(res_df, metric)

        metric_values[disp_name] = tmp

    return prompt_completions_dict, metric_values
    

def get_b64_boxplot(res_by_metric, metric, xlabel):
    buffer = BytesIO()

    labels, values = zip(*res_by_metric[['elem_id', metric]].values)
    fig, ax = plt.subplots()

    sns.boxplot(
        data=values,
        orient='h',
        palette='Set3',
        width=0.25,
        showfliers=False,
        ax=ax
    )

    sns.stripplot(data=values, orient='h', jitter=False, color='black', ax=ax)

    ax.set_xlabel(xlabel, labelpad=10)
    ax.set_ylabel('Prompt #', labelpad=10)
    ax.set_yticklabels(labels)

    fig.savefig(buffer, format='svg', bbox_inches='tight')
    b64_raw = base64.b64encode(buffer.getvalue())
    return str(b64_raw)[2:-1]


def get_table_components(res_df, metric):
    tab = res_df.groupby(['elem_id'])[metric].describe()
    tab = tab.drop(columns=['count', '25%', '75%']).rename(columns={'elem_id': 'Prompt #', '50%': "median"})
    headers = list(tab.columns)
    values = tab.T.to_dict()
    return headers, values
