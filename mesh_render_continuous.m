% Renders a 3D nii file specified by V

function mesh_render(V,mesh_white,mesh_inflated,axle)

if ~exist('axel','var')
    axle=[0 90];
end;

for hemiind_rend=1:2
    % Sample back in as surface
    co=V.mat\double([mesh_white{hemiind_rend}.vertices' ; ones(1,size(mesh_white{hemiind_rend}.vertices,1))]);
    vertclass=spm_sample_vol(V,co(1,:),co(2,:),co(3,:),0);
    cdata=0.25*ones(size(mesh_white{hemiind_rend}.vertices,1),3);
    cdata(vertclass<0,3)=-vertclass(vertclass<0)*0.75+0.25;
    cdata(vertclass>0,1)=vertclass(vertclass>0)*0.75+0.25;
    cdata(cdata>1)=1;
    cdata(cdata<0.25)=0.25;
    
    axis equal
    axis off
    
    hp = patch(struct('Parent',gca,'vertices',mesh_inflated{hemiind_rend}.vertices,'faces',mesh_inflated{hemiind_rend}.faces, ...
        'edgecolor','none','FaceColor','interp','FaceVertexCdata',cdata));
    
end;
view(axle);
camlight;
camlight(-80,70);
material([0.5 1 0.3]);