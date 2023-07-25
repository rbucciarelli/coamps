%% NAME: plot_coamps.m
%- DESC: Plot data from COAMPS netcdf files
%--------------------------------------------------------------------------

clear all; %close all;

%% Input parameters
lat_lims = [36 39];
lon_lims = [-125 -121];

%% Initialize vars
D = {};
ncfile = './coamps_cencoos_subset.nc';

%% Attempt to connect to ncfile, if fail return
try
    meta = ncinfo(ncfile);
catch
    disp(['Could not open file: ' ncfile]);
    return;
end
    
%% Read in variables defining spatio-temporal extents
lons = double(ncread(ncfile,'longitude'));  %- -180:1:180 (W --> E)
lats = double(ncread(ncfile,'latitude'));   %- 90:1:-90 (N --> S)
times = ncread(ncfile,'time');
wnd_utru = double(ncread(ncfile,'wnd_utru')); 
wnd_vtru = double(ncread(ncfile,'wnd_vtru')); 

%% Convert times to datenum
time_atts = meta.Variables(1).Attributes(1).Value;   % 'hours since 2022-05-29T00:00:00Z'
time_atts = split(time_atts);
T0 = char(join(time_atts{3}(1:10),time_atts{3}(12:end-1)));  % '2022-05-29 00:00:00'
%T0 = '1900-01-01 00:00:00.0';
T0 = datenum(T0);
mtimes = double(times)/24 + T0;


%% Grid up lat/lons
[xi,yi] = meshgrid(lats,lons);

%% Find cell w/ maximum u-winds to plot time-series
[C,I] = max(wnd_utru(:));
[i,j,k] = ind2sub(size(wnd_utru),I);
x0 = lons(i);
y0 = lats(j);
t0 = times(k);


%%- Grab high-resolution coastline that ships w/ matlab
filename = gunzip("gshhs_c.b.gz",'.');
S = gshhs(filename{1});

%% Plot up u-array and time-series of one cell
figure
subplot(2,1,1)
pcolor(yi,xi,squeeze(wnd_utru(:,:,1)))
shading flat
hold on;
plot([S.Lon],[S.Lat],'k');
plot(x0,y0,'r*','MarkerSize',15)
xlabel('Longitude')
ylabel('Latitude')
title(['COAMPS ' datestr(mtimes(k),'dd-mmm-yyyyTHH:MM:SS') ]);

subplot(2,1,2)
plot(mtimes,squeeze(wnd_utru(i,j,:)))
ylabel('Wind U (m/s)');
xlabel('Time (UTC)');
axis tight
set(gca,'XTickLabel',datestr(get(gca,'XTick'),'mm-dd'))
