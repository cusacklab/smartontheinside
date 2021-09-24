% Renders a 3D nii file specified by V

function mesh_render(V,mesh_white,mesh_inflated)


for hemiind_rend=1:2
    % Sample back in as surface
    co=V.mat\double([mesh_white{hemiind_rend}.vertices' ; ones(1,size(mesh_white{hemiind_rend}.vertices,1))]);
    vertclass=round(spm_sample_vol(V,co(1,:),co(2,:),co(3,:),0));
    cdata=0.25*ones(size(mesh_white{hemiind_rend}.vertices,1),3);
    cdata(vertclass==1,3)=1;
    cdata(vertclass==2,1)=1;
    axis equal
    axis off
    
    hp = patch(struct('Parent',gca,'vertices',mesh_inflated{hemiind_rend}.vertices,'faces',mesh_inflated{hemiind_rend}.faces, ...
        'edgecolor','none','FaceColor','interp','FaceVertexCdata',cdata));
    
end;
view(0,-90);
camlight;
camlight(-80,-10);
material([0.5 0.5 0.3]);