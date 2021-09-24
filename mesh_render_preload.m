function [mesh_white,mesh_inflated]=mesh_render_preload(hcppath)
fshemilab={'L','R'};
clear mesh_white
clear mesh_inflated
for hemiind_rend=1:2
    mesh_white{hemiind_rend}=gifti(fullfile(hcppath,sprintf('Q1-Q6_RelatedParcellation210.%s.white_MSMAll_2_d41_WRN_DeDrift.32k_fs_LR.surf.gii',fshemilab{hemiind_rend})));
    mesh_inflated{hemiind_rend}=gifti(fullfile(hcppath,sprintf('Q1-Q6_RelatedParcellation210.%s.inflated_MSMAll_2_d41_WRN_DeDrift.32k_fs_LR.surf.gii',fshemilab{hemiind_rend})));
end;