vertclass=[-3:0.05:3]';

cdata=0.25*ones(length(vertclass),1,3);
cdata(vertclass<0,:,3)=-vertclass(vertclass<0)*0.75+0.25;
cdata(vertclass>0,:,1)=vertclass(vertclass>0)*0.75+0.25;
figure;
imagesc(cdata)
axis xy
axis off