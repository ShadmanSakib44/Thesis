import os
import pandas as pd
import nltk
from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from bert_score import score as bert_score

# ——— Ensure NLTK data is present ———
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

def load_column(path: str, column: str, n_samples: int) -> list[str]:
    """Read CSV and return the first n_samples of the given column as strings."""
    df = pd.read_csv(path)
    if column not in df.columns:
        raise KeyError(f"Column '{column}' not found in {path!r}")
    return df[column].fillna('').astype(str).head(n_samples).tolist()

def compute_metrics(
    refs: list[str],
    preds: list[str],
    lang: str = 'en',
) -> dict[str, float]:
    """
    Compute average ROUGE-L, BLEU (smoothed), and BERTScore F1
    between parallel lists of refs and preds.
    """
    # ROUGE-L scorer
    rouge = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
    smooth_fn = SmoothingFunction().method1

    # BERTScore (vectorized)
    P, R, F1 = bert_score(preds, refs, lang=lang, verbose=False)

    # Per-example ROUGE-L and BLEU
    rouge_l_scores = []
    bleu_scores     = []

    for r, p in zip(refs, preds):
        rouge_l_scores.append(rouge.score(r, p)['rougeL'].fmeasure)
        rtok = nltk.word_tokenize(r)
        ptok = nltk.word_tokenize(p)
        bleu_scores.append(sentence_bleu([rtok], ptok, smoothing_function=smooth_fn))

    return {
        'rougeL':     sum(rouge_l_scores) / len(rouge_l_scores),
        'bleu':       sum(bleu_scores)     / len(bleu_scores),
        'bertscore': float(F1.mean()),
    }

def summarize_all(
    gt_path: str,
    output_dir: str,
    output_files: list[str],
    gt_col: str = 'user-story',
    pred_col: str = 'generated_user_story',
    n_samples: int = 100,
) -> pd.DataFrame:
    """
    Load ground truth and each predictions file, compute metrics,
    and return a DataFrame summary.
    """
    # Load references once
    refs = load_column(gt_path, gt_col, n_samples)

    records = []
    for fname in output_files:
        model_name = os.path.splitext(fname)[0]
        full_path  = os.path.join(output_dir, fname)
        preds      = load_column(full_path, pred_col, n_samples)

        metrics = compute_metrics(refs, preds)
        records.append({
            'model':      model_name,
            'avg_rougeL': metrics['rougeL'],
            'avg_bleu':   metrics['bleu'],
            'avg_bertscore_f1': metrics['bertscore'],
        })

    return pd.DataFrame.from_records(records)

if __name__ == '__main__':
    # ——— Configuration ———
    ground_truth_file = r'D:\Research\Thesis\Organized\filtered_22-4-2025.csv'
    outputs_dir       = r'D:\Research\Thesis\Organized\Outputs'
    outputs_list      = [
        'gemini2_flash_user_stories_one_shot.csv',
        'gemini2_flash_user_stories_zero_shot.csv',
        'gpt3.5_turbo_user_stories_two_shot.csv',
        'gpt3.5_turbo_user_stories_zero_shot.csv',
        'gpt3.5turbo_user_stories_one_shot.csv',
        'mistral_user_stories_zero_shot.csv',
    ]

    # ——— Run and show summary ———
    summary_df = summarize_all(
        ground_truth_file,
        outputs_dir,
        outputs_list,
        gt_col='user-story',
        pred_col='generated_user_story',
        n_samples=100,
    )

    print("\nMetric summary (first 100 examples):\n")
    print(summary_df.to_string(index=False, float_format='%.4f'))
