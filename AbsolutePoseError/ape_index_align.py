import numpy as np
import matplotlib.pyplot as plt
from evo.tools import file_interface
from evo.core.trajectory import PoseTrajectory3D
from evo.core import metrics
import copy

def subsample_to_length(traj: PoseTrajectory3D, target_len: int):
    idxs = np.linspace(0, len(traj.positions_xyz) - 1, target_len).astype(int)
    return PoseTrajectory3D(
        positions_xyz=traj.positions_xyz[idxs],
        orientations_quat_wxyz=traj.orientations_quat_wxyz[idxs],
        timestamps=np.arange(target_len)
    )

# Load TUM trajectories
ref_traj = file_interface.read_tum_trajectory_file("ground_truth.tum")
est_traj = file_interface.read_tum_trajectory_file("trajectory.tum")

# Determine which is longer
len_ref = len(ref_traj.positions_xyz)
len_est = len(est_traj.positions_xyz)

if len_ref < len_est:
    est_traj_resampled = subsample_to_length(est_traj, len_ref)
    ref_traj_resampled = PoseTrajectory3D(
        positions_xyz=ref_traj.positions_xyz,
        orientations_quat_wxyz=ref_traj.orientations_quat_wxyz,
        timestamps=np.arange(len_ref)
    )
else:
    ref_traj_resampled = subsample_to_length(ref_traj, len_est)
    est_traj_resampled = PoseTrajectory3D(
        positions_xyz=est_traj.positions_xyz,
        orientations_quat_wxyz=est_traj.orientations_quat_wxyz,
        timestamps=np.arange(len_est)
    )

# Apply Umeyama alignment with scale correction
aligned_est = copy.deepcopy(est_traj_resampled)
aligned_est.align(ref_traj_resampled, correct_scale=True)

# Compute APE
ape = metrics.APE(metrics.PoseRelation.full_transformation)
ape.process_data((ref_traj_resampled, aligned_est))

# Print stats
print("\n=== Absolute Pose Error (APE) ===")
for k, v in ape.get_all_statistics().items():
    print(f"{k:<10}: {v:.6f}")

# Plot
plt.figure(figsize=(8, 6))
plt.plot(ref_traj_resampled.positions_xyz[:, 0], ref_traj_resampled.positions_xyz[:, 1], label="Ground Truth", linewidth=2)
plt.plot(aligned_est.positions_xyz[:, 0], aligned_est.positions_xyz[:, 1], label="Estimated (Aligned)", linewidth=2)
plt.legend()
plt.title("Aligned Trajectories (XY Plane)")
plt.xlabel("X (m)")
plt.ylabel("Y (m)")
plt.axis("equal")
plt.grid(True)
plt.tight_layout()
plt.savefig("aligned_ape_plot.pdf")
plt.show()