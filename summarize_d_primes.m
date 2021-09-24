%% Summarize d-primes

summary_results_path='/imaging/rcusack/laura_ffa_diffusion/summary_results';

grouplist={'adults','infants'};
seedregionlabels={'faces','places','tools'};
hemilab={'left','right'};

dprime={};
nsubj=[];
for groupind=1:length(grouplist)
    switch grouplist{groupind}
        case 'adults'
            adult_s2t=load(fullfile(summary_results_path,'adult_s2t'));
            seedresults=adult_s2t.a2a_seedresults;
        case 'infants'
            infant_s2t=load(fullfile(summary_results_path,'trainadult_testinfant.mat'));
            seedresults=infant_s2t.a2i_seedresults;
    end;
    
    nseedregion=size(seedresults,1);
    nsubj(groupind)=size(seedresults,2);
    
    dprime{groupind}=nan(nseedregion,nsubj(groupind),2);
    
    for seedregionind=1:nseedregion
        for hemiind=1:2
            for subjind=1:nsubj(groupind)
                hits=seedresults{seedregionind,subjind,hemiind}.hits;
                fa=seedresults{seedregionind,subjind,hemiind}.fa;
                hits(hits==1)=1-0.5/sum(seedresults{seedregionind,subjind,hemiind}.testlabels==1);
                hits(hits==0)=0.5/sum(seedresults{seedregionind,subjind,hemiind}.testlabels==1);
                fa(fa==0)=0.5/sum(seedresults{seedregionind,subjind,hemiind}.testlabels==1);
                fa(fa==1)=1-0.5/sum(seedresults{seedregionind,subjind,hemiind}.testlabels==1);
                dprime{groupind}(seedregionind,subjind,hemiind)=norminv(hits)-norminv(fa);
            end;
        end;
    end;
end;

%% Graph up
figure(10)
clf
for groupind=1:2
    errorbar(squeeze(mean(dprime{groupind},2)), squeeze(std(dprime{groupind},[],2))/sqrt(nsubj(groupind)))
    hold on
end;
legend({'adult-L','adult-R','infant-L','infant-R'});

%% Stats
for groupind=1:2
    fprintf('Group %s\n',grouplist{groupind});
    for seedregionind=1:nseedregion 
        for hemiind=1:2            
            [h p]=ttest(squeeze(dprime{groupind}(seedregionind,:,hemiind)));
            fprintf('    Region %s %s p<%f\n',seedregionlabels{seedregionind},hemilab{hemiind},p);
        end;
    end;
end;

%% Graph individuals
figure(22);
for groupind=1:2
    subplot(2,1,groupind)
    bar(mean(dprime{groupind},3));
    title(grouplist{groupind})
    ylabel('d-prime of classification')
    set(gca,'XTick',1:3);
    set(gca,'XTickLabel',seedregionlabels);
    ylim([-1 2.75])
end;
