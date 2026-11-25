import database_construction as dc
import import_table as it
import recommendation as rc

""" Step1 : Construct Sample Database"""
dc.construct_db("../test/sample.db")

""" Step2 : Import Tables to Sample Database"""
it.import_csv_to_db(CSV_FOLDER = "../data",TARGET_DB = "../test/sample.db")

""" Step3 : Run Recommendation for 1529 authors"""
rc.recommendation(output_dir = "../test",
    train_csv_path = "../data/train_test/train.csv",
    test_csv_path = "../data/train_test/test.csv",
    database_path="../test/sample.db")









