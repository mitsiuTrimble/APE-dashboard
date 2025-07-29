import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from evo.tools import file_interface
from evo.core.trajectory import PoseTrajectory3D
from evo.core import metrics
import copy
import json
import csv
import pandas as pd

def convert_csv_to_tum(input_path):
    output_path = os.path.splitext(input_path)[0] + ".tum"
    with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:
        lines = infile.readlines()
        # Skip first 2 header/comment lines
        data_lines = lines[2:]
        for line in data_lines:
            line = line.strip()
            if line:
                outfile.write(line + '\n')
    return output_path

def convert_txt_to_tum(input_path):
    output_path = os.path.splitext(input_path)[0] + ".tum"
    with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:
        for line in infile:
            line = line.strip()
            if line:
                outfile.write(line + '\n')
    return output_path

def subsample_to_length(traj: PoseTrajectory3D, target_len: int):
    idxs = np.linspace(0, len(traj.positions_xyz) - 1, target_len).astype(int)
    return PoseTrajectory3D(
        positions_xyz=traj.positions_xyz[idxs],
        orientations_quat_wxyz=traj.orientations_quat_wxyz[idxs],
        timestamps=np.arange(target_len)
    )

def is_valid_tum_file(filepath):
    try:
        with open(filepath, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 8:
                    return True  # Found a valid pose line
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    return False  # No valid line found


def compute_ape_and_plot(gt_tum_path, est_tum_path, output_plot_path):
    print(f"Loading trajectories:\n - GT: {gt_tum_path}\n - Est: {est_tum_path}")
    ref_traj = file_interface.read_tum_trajectory_file(gt_tum_path)
    est_traj = file_interface.read_tum_trajectory_file(est_tum_path)

    len_ref = len(ref_traj.positions_xyz)
    len_est = len(est_traj.positions_xyz)

    if len_ref < len_est:
        est_resampled = subsample_to_length(est_traj, len_ref)
        ref_resampled = PoseTrajectory3D(
            positions_xyz=ref_traj.positions_xyz,
            orientations_quat_wxyz=ref_traj.orientations_quat_wxyz,
            timestamps=np.arange(len_ref)
        )
    else:
        ref_resampled = subsample_to_length(ref_traj, len_est)
        est_resampled = PoseTrajectory3D(
            positions_xyz=est_traj.positions_xyz,
            orientations_quat_wxyz=est_traj.orientations_quat_wxyz,
            timestamps=np.arange(len_est)
        )

    aligned_est = copy.deepcopy(est_resampled)
    aligned_est.align(ref_resampled, correct_scale=True)

    ape_metric = metrics.APE(metrics.PoseRelation.full_transformation)
    ape_metric.process_data((ref_resampled, aligned_est))

    stats = ape_metric.get_all_statistics()
    print(f"APE stats: {stats}")

    # Plot trajectories XY plane
    plt.figure(figsize=(8,6))
    plt.plot(ref_resampled.positions_xyz[:,0], ref_resampled.positions_xyz[:,1], label="Ground Truth", linewidth=2)
    plt.plot(aligned_est.positions_xyz[:,0], aligned_est.positions_xyz[:,1], label="Estimated (Aligned)", linewidth=2)
    plt.legend()
    plt.title("Aligned Trajectories (XY Plane)")
    plt.xlabel("X (m)")
    plt.ylabel("Y (m)")
    plt.axis("equal")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_plot_path)
    plt.close()
    print(f"✅ Plot saved to {output_plot_path}")

    return stats


def find_trajectory_files(folder_path):
    """
    Return list of trajectory files (.csv or .txt) in folder_path (non-recursive)
    """
    files = []
    for f in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, f)) and f.lower().endswith(('.csv','.txt')):
            files.append(f)
    return files

def safe_filename(s):
    # Replace os.sep and spaces with underscores for safe filenames
    return s.replace(os.sep, "_").replace(" ", "_")

def main(root_folder, result_folder, output_folder):
    master_excel = '/home/tpc/Downloads/atlasDataMasterfile.xlsx'
    sheets_dict = pd.read_excel(master_excel, sheet_name=None)

    # df_sheet1 = sheets_dict["Sheet1"]

    for dataset in sheets_dict:
        if dataset == 'FloorPlans': continue
        dataset = 'NWC' if dataset == 'National Western Campus' else dataset
                
        cur_dataset = sheets_dict[dataset]
        cur_dataset['Link to 360 Video'] = cur_dataset['Link to 360 Video'].apply(
                            lambda x: x.strip()[:19] + x.strip()[22:26] 
                            if isinstance(x, str) 
                            else x
                            )

    gt_root = os.path.join(root_folder, "groundTruth")
    if not os.path.isdir(gt_root):
        print(f"GroundTruth folder not found in {gt_root}")
        return

    os.makedirs(output_folder, exist_ok=True)
    plot_dir = os.path.join(output_folder, "plots")
    os.makedirs(plot_dir, exist_ok=True)

    results = []
    for dataset in os.listdir(gt_root):
        cur_dataset = 'NWC' if dataset == 'National Western Campus' else dataset
        cur_dataset = 'Buchs IT' if dataset == 'Buchs IT Site' else dataset
        if dataset == 'E&K': continue
        print(f"cur_dataset: {cur_dataset}")
        dataset_df = sheets_dict[cur_dataset] if dataset in sheets_dict else None
                

        dataset_vid_path = os.path.join(gt_root, dataset)
        resolution_list = os.listdir(os.path.join(result_folder, dataset))

        vid_pairs = []
        for vid in os.listdir(dataset_vid_path):
            if not os.path.isdir(os.path.join(dataset_vid_path, vid)): continue

            # manually remove certain videos:
            if dataset == 'NREL' and vid in ['VID_20250425_102029_046', 'VID_20250509_100905_046']: continue
            
            # remove timlapse/timeshift
            if dataset_df is not None:
                cur_mode = dataset_df.loc[dataset_df['Link to 360 Video'] == vid, 'Mode']
                if not cur_mode.empty and cur_mode.str.contains("Timelapse|Timeshift", case=False, na=False).any():
                    continue

            gt_vid_list = [os.path.join(dataset_vid_path, vid, f) for f in os.listdir(os.path.join(dataset_vid_path, vid))
                        if f.lower().endswith(('.csv','.txt'))]

            #TODO: maybe not just use idx 0
            if len(gt_vid_list) <= 0: continue
            gt_vid = gt_vid_list[0]

            resolute_vid_dict = {}
            for resolution in resolution_list:
                algo_folders = [f for f in os.listdir(os.path.join(result_folder, dataset, resolution)) 
                                if os.path.isdir(os.path.join(result_folder, dataset, resolution, f))]
                
                for algo in algo_folders:
                    res_traj_file = os.path.join(result_folder, dataset, resolution, algo, vid, "frame_trajectory.txt")
                    if os.path.exists(res_traj_file):
                        vid_pairs.append((gt_vid, res_traj_file))

        print(f"data: {dataset} vid pair: {len(vid_pairs)}")

        for gt_file, res_traj_file in vid_pairs:
            # Convert to tum
            if gt_file.lower().endswith('.csv'):
                gt_tum = convert_csv_to_tum(gt_file)
            else:
                gt_tum = convert_txt_to_tum(gt_file)

            if res_traj_file.lower().endswith('.csv'):
                algo_tum = convert_csv_to_tum(res_traj_file)
            else:
                algo_tum = convert_txt_to_tum(res_traj_file)

            if not is_valid_tum_file(gt_tum):
                print(f"Skipping: Empty or invalid GT TUM file: {gt_tum}")
                continue
            if not is_valid_tum_file(algo_tum):
                print(f"Skipping: Empty or invalid Algo TUM file: {algo_tum}")
                continue
            
            algo_path = os.path.dirname(res_traj_file) # absolute path
            safe_rel_path = safe_filename('/'.join(algo_path.split('/')[4:]))
            print(f"algo_path: {algo_path} and safe_rel_path: {safe_rel_path}")
            plot_fname = f"{safe_rel_path}_EST_{os.path.basename(res_traj_file).split('.')[0]}_vs_GT_{os.path.basename(gt_file)}.pdf"
            plot_path = os.path.join(plot_dir, plot_fname)
            print(f"plot_path; {plot_path}")
            
            ## Compute APE and plot
            ape_stats = compute_ape_and_plot(gt_tum, algo_tum, plot_path)

            results.append({
                "algorithm": algo_path.split('/')[-2].split('_')[0],
                "algorithm_relative_folder": '/'.join(algo_path.split('/')[4:]),
                "folder": os.path.basename(os.path.dirname(res_traj_file)),
                "algo_file": os.path.basename(res_traj_file),
                "gt_file": os.path.basename(gt_file),
                **ape_stats,
                "plot_path": plot_path
            })
            

    if not results:
        print("No results generated.")
        return

    # Save results CSV
    csv_path = os.path.join(output_folder, "ape_results.csv")
    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = list(results[0].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(r)

    # Save results JSON
    json_path = os.path.join(output_folder, "ape_results.json")
    with open(json_path, 'w') as jf:
        json.dump(results, jf, indent=4)

    print(f"✅ Finished processing {len(results)} trajectory pairs.")
    print(f"Results saved to:\n - {csv_path}\n - {json_path}")
    print(f"Plots saved in folder:\n - {plot_dir}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_batch_ape.py /path/to/root_folder /path/to/result [output_folder]")
        sys.exit(1)
    root_folder = sys.argv[1]
    result_folder = sys.argv[2]
    output_folder = sys.argv[3] if len(sys.argv) > 2 else os.path.join(root_folder, "ape_results")
    main(root_folder, result_folder, output_folder)