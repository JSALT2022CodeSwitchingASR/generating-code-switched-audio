cp -r data/train data/train_mono
python local/add_lid_seame_v2.py --src data/train/text
python local/subset_seame_mono.py --src data/train --dst data/train_mono