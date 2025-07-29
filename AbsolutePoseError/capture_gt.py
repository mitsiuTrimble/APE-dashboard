import os
import sys
import yaml
import shutil


def get_all_gt(dataset, gt_google_dir):
	file_dict = dict()
	gt_google_org = os.path.join(gt_google_dir, dataset, "Exyn Scans")
	for date_dir in os.listdir(gt_google_org):
		gt_goog_date = os.path.join(gt_google_org, date_dir)

		for file in os.listdir(gt_goog_date):
			if file.endswith('.traj.csv'):
				date_split_list = file.split('.')
				date = ''.join(date_split_list[0].split('_'))
				time = ''.join(date_split_list[1].split('_')[:2])
				date_time = date + "_" + time
				file_dict[date_time] = os.path.join(gt_goog_date, file)

	return file_dict





def mkdir_gt(videos_dir, dataset_list, target_dir, gt_google_dir):
	for dataset in dataset_list:
		gt_file_dict = get_all_gt(dataset, gt_google_dir)


		dataset_fullpath = os.path.join(videos_dir, dataset)
		resolution_list = [r for r in os.listdir(dataset_fullpath) if os.path.isdir(os.path.join(dataset_fullpath, r))]

		for resolution in resolution_list:
			resolution_fullpath = os.path.join(dataset_fullpath, resolution)

			subfolders = [f for f in os.listdir(resolution_fullpath) if os.path.isdir(os.path.join(resolution_fullpath, f))]

			if len(subfolders) > 0:
				subfolder = subfolders[0]
				vids_fullpath = os.path.join(resolution_fullpath, subfolder)
				vid_subfolders = [f for f in os.listdir(vids_fullpath) if os.path.isdir(os.path.join(vids_fullpath, f))]

				for vid_f in vid_subfolders:
					if dataset == 'National Western Campus': dataset = 'NWC'
					desc_path = os.path.join(target_dir, dataset, vid_f)
					os.makedirs(desc_path, exist_ok=True)

					try:
						key_vid = vid_f[4:4+13]  # Extract 'YYYYMMDD_HHMM'
						print(f"dataset {dataset} key: {key_vid}")
						# if dataset == 'Trimble Christchurch': key_vid[7] = str(int(key_vid[7]) - 1)
						gt_file_loc = gt_file_dict[key_vid]  # Lookup from dictionary
						print(f"{vid_f} to {gt_file_loc}")
					except KeyError:
						print(f"⚠️ Dataset {dataset} Key not found for {vid_f} with key {key_vid}")
						continue
					except Exception as e:
						print(f"❌ Error while accessing ground truth file: {e}")
						continue

					# copy to vid_f
					try:
						print(f"📁 Copying {gt_file_loc} to {desc_path}")
						shutil.copy(gt_file_loc, desc_path)  # Actually copy the file
					except Exception as e:
						print(f"❌ Failed to copy {gt_file_loc} to {desc_path} — {e}")





			continue




if __name__ == "__main__":
    videos_dir = "/home/tpc/Atlas Results"
    gt_google_dir = '/media/tpc/Extreme SSD/GoogleDrive'
    target_desc_dir = "/home/tpc/Downloads/BenchmarkingSnippets/APE_dashboard_Updated/AbsolutePoseError/groundTruth"
    dataset_list = [d for d in os.listdir(videos_dir) if os.path.isdir(os.path.join(videos_dir, d))]


    mkdir_gt(videos_dir, ['NREL', 'National Western Campus', 'Trimble Christchurch'], 
    			target_desc_dir, gt_google_dir)