from scripts.build import load_clean, model_checks


def test_data_and_cleaning():
    df = load_clean()
    assert len(df) == 374
    assert set(df["Sleep Disorder"]) == {"None", "Insomnia", "Sleep Apnea"}
    assert set(df["BMI Category"]) == {"Normal", "Overweight", "Obese"}
    assert (df["BP Systolic"] > df["BP Diastolic"]).all()


def test_model_results_match_notebook():
    r = model_checks(load_clean())
    assert r["original_split"]["accuracy"] == 0.88                  # the notebook's 88.0%
    assert r["original_split"]["test_rows_also_in_training"] == 66
    assert r["group_kfold"]["mean_accuracy"] > 0.85                  # holds on unseen profiles
    assert r["unique_profiles_cv"]["mean_accuracy"] > r["unique_profiles_baseline"]
