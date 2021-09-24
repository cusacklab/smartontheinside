2017-04-13 
= Typical analysis, adults =
(1) Run aa user script ----.m but only stages as far as bedpostx are needed
(2) 

= Summary of files =

infant_probtrackx and adult_probtrackx
    Use FA with TBSS for normalisation.. back normalise ROIs, run probtrackx in each individual and then normalise output

adult_s2t_v1.m and infant_s2t_v1.m
    Read in output of probtrackx to produce [subjects x target_region x seed_voxel] summary matrix

s2t_toptargets.m & s2t_toptargets_v2.m
    ?? I think ?? Run classifier to relate connectivity pattern to regions
trainadult_testinfant.m
    ?? I think ?? Apply adult classification to infants 
summarize_d_primes.m
    Summarize classification results

split labelled ROI for use with probtrackx?
    makerois.m

junk I think
    infant_s2t_check.m s2t_ica.m s2t_infant.m

For rendering
    connection_colorbar.m
    mesh_render_continuous.m
    mesh_render.m
    mesh_render_preload.m

Laura to describe
    ContrastSeed.m
    ContrastSeed_v2.m
    MMtoVox2.m
    MMtoVox2_SeedROI.m
    MMtoVox.m
    MMtoVox_Target.m
    SupNeuroRegion.m
    VentralVisualStream.m
    VentralVisualStream_v2.m

