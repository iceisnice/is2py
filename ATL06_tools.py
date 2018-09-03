import h5py
import numpy as np

from is2_utils import *

from bokeh.layouts import gridplot
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.io import output_notebook, push_notebook, show, output_file
output_notebook(INLINE)

"""
Basic tools to read and plot ICESat-2 data
Created by Susheel, with code input from Ben Smith.

"""

def read_atl06(filename,beam_names=None):

    if beam_names is None:
        beam_names = ['gt1l','gt1r','gt2l','gt2r','gt3l','gt3r']

    h5_f = h5py.File(filename,'r')

    h = nested_dict() #Empty dictionary - is this the most memory efficient way?
    for beam_name in beam_names:

        #List of fields to read: Basic stuff for now, just for debugging
        h[beam_name]['h_li'] = np.array(h5_f[beam_name]['land_ice_segments']['h_li']).transpose()
        h[beam_name]['h_li'][h[beam_name]['h_li'] > 1.0e10] = np.nan
        h[beam_name]['h_li_sigma'] = np.array(h5_f[beam_name]['land_ice_segments']['h_li_sigma']).transpose()
        h[beam_name]['lat_li'] = np.array(h5_f[beam_name]['land_ice_segments']['latitude']).transpose()
        h[beam_name]['lon_li'] = np.array(h5_f[beam_name]['land_ice_segments']['longitude']).transpose()
        h[beam_name]['atl06_quality_summary'] = np.array(h5_f[beam_name]['land_ice_segments']['atl06_quality_summary']).transpose()
        h[beam_name]['segment_id'] = np.array(h5_f[beam_name]['land_ice_segments']['segment_id']).transpose()
        t_off = np.array(h5_f['ancillary_data']['atlas_sdp_gps_epoch']).transpose()
        h[beam_name]['delta_time'] = gps_time_to_fracyr(np.array(h5_f[beam_name]['land_ice_segments']['delta_time']).transpose() + t_off)
        h[beam_name]['h_robust_spread'] = np.array(h5_f[beam_name]['land_ice_segments']['fit_statistics']['h_robust_sprd']).transpose()
        h[beam_name]['snr_significance'] = np.array(h5_f[beam_name]['land_ice_segments']['fit_statistics']['snr_significance']).transpose()
        h[beam_name]['signal_selection_source'] = np.array(h5_f[beam_name]['land_ice_segments']['fit_statistics']['signal_selection_source']).transpose()

        h[beam_name]['x_li'], h[beam_name]['y_li'] = ll2ps(h[beam_name]['lon_li'], h[beam_name]['lat_li'], slat=71, slon=0, hemi='s', units='m')

    return h

def read_atl03(filename,beam_names=None):

    if beam_names is None:
        beam_names = ['gt1l','gt1r','gt2l','gt2r','gt3l','gt3r']

    h5_f = h5py.File(filename,'r')

    h = nested_dict() #Empty dictionary - is this the most memory efficient way?
    for beam_name in beam_names:

        #List of fields to read: Basic stuff for now, just for debugging
        h[beam_name]['h_ph'] = np.array(h5_f[beam_name]['heights']['h_ph']).transpose()
        h[beam_name]['h_ph'][h[beam_name]['h_ph'] > 1.0e10] = np.nan
        h[beam_name]['lat_ph'] = np.array(h5_f[beam_name]['heights']['lat_ph']).transpose()
        h[beam_name]['lon_ph'] = np.array(h5_f[beam_name]['heights']['lon_ph']).transpose()
        t_off = np.array(h5_f['ancillary_data']['atlas_sdp_gps_epoch']).transpose()
        h[beam_name]['delta_time'] = gps_time_to_fracyr(np.array(h5_f[beam_name]['heights']['delta_time']).transpose() + t_off)
        h[beam_name]['dist_ph_along'] = np.array(h5_f[beam_name]['heights']['dist_ph_along']).transpose()
        h[beam_name]['ph_id_channel'] = np.array(h5_f[beam_name]['heights']['ph_id_channel']).transpose()
        h[beam_name]['x_ph'], h[beam_name]['y_ph'] = ll2ps(h[beam_name]['lon_ph'], h[beam_name]['lat_ph'], slat=71, slon=0, hemi='s', units='m')
        h[beam_name]['segment_id'] = np.array(h5_f[beam_name]['geolocation']['segment_id']).transpose()

    return h

def plot_atl06(h,hold='off',x_axis='x_li',atl06_handle=None):

    if atl06_handle is None:
        s1 = figure(plot_width=500, plot_height=200, title='gt1l')
        s2 = figure(plot_width=500, plot_height=200, x_range=s1.x_range, y_range=s1.y_range, title='gt1r')
        s3 = figure(plot_width=500, plot_height=200, x_range=s1.x_range, y_range=s1.y_range, title='gt2l')
        s4 = figure(plot_width=500, plot_height=200, x_range=s1.x_range, y_range=s1.y_range, title='gt2r')
        s5 = figure(plot_width=500, plot_height=200, x_range=s1.x_range, y_range=s1.y_range, title='gt3l')
        s6 = figure(plot_width=500, plot_height=200, x_range=s1.x_range, y_range=s1.y_range, title='gt3r')
        atl06_handle = [s1,s2,s3,s4,s5,s6]

    atl06_handle[0].circle(h['gt1l'][x_axis],h['gt1l']['h_li'], size=1, color="navy", alpha=1.0)
    atl06_handle[1].circle(h['gt1r'][x_axis],h['gt1r']['h_li'], size=1, color="navy", alpha=1.0)
    atl06_handle[2].circle(h['gt2l'][x_axis],h['gt2l']['h_li'], size=1, color="firebrick", alpha=1.0)
    atl06_handle[3].circle(h['gt2r'][x_axis],h['gt2r']['h_li'], size=1, color="firebrick", alpha=1.0)
    atl06_handle[4].circle(h['gt3l'][x_axis],h['gt3l']['h_li'], size=1, color="olive", alpha=1.0)
    atl06_handle[5].circle(h['gt3r'][x_axis],h['gt3r']['h_li'], size=1, color="olive", alpha=1.0)

    p = gridplot([[atl06_handle[0],atl06_handle[1]], [atl06_handle[2],atl06_handle[3]], [atl06_handle[4],atl06_handle[5]]])

    # show the results
    if hold is 'off':
        output_file("atl03-06_plot.html", title="atl03-06_plot")
        show(p)
    else:
        return [s1,s2,s3,s4,s5,s6]

def plot_atl03(h,hold='off',x_axis='x_ph',decimate=50,atl06_handle=None):

    if atl06_handle is None:
        s1 = figure(plot_width=500, plot_height=200, title='gt1l')
        s2 = figure(plot_width=500, plot_height=200, x_range=s1.x_range, y_range=s1.y_range, title='gt1r')
        s3 = figure(plot_width=500, plot_height=200, x_range=s1.x_range, y_range=s1.y_range, title='gt2l')
        s4 = figure(plot_width=500, plot_height=200, x_range=s1.x_range, y_range=s1.y_range, title='gt2r')
        s5 = figure(plot_width=500, plot_height=200, x_range=s1.x_range, y_range=s1.y_range, title='gt3l')
        s6 = figure(plot_width=500, plot_height=200, x_range=s1.x_range, y_range=s1.y_range, title='gt3r')
        atl06_handle = [s1,s2,s3,s4,s5,s6]

    atl06_handle[0].circle(h['gt1l'][x_axis][1::decimate],h['gt1l']['h_ph'][1::decimate], size=0.1, color="black", alpha=0.7)
    atl06_handle[1].circle(h['gt1r'][x_axis][1::decimate],h['gt1r']['h_ph'][1::decimate], size=0.1, color="black", alpha=0.7)
    atl06_handle[2].circle(h['gt2l'][x_axis][1::decimate],h['gt2l']['h_ph'][1::decimate], size=0.1, color="black", alpha=0.7)
    atl06_handle[3].circle(h['gt2r'][x_axis][1::decimate],h['gt2r']['h_ph'][1::decimate], size=0.1, color="black", alpha=0.7)
    atl06_handle[4].circle(h['gt3l'][x_axis][1::decimate],h['gt3l']['h_ph'][1::decimate], size=0.1, color="black", alpha=0.7)
    atl06_handle[5].circle(h['gt3r'][x_axis][1::decimate],h['gt3r']['h_ph'][1::decimate], size=0.1, color="black", alpha=0.7)

    p = gridplot([[atl06_handle[0],atl06_handle[1]], [atl06_handle[2],atl06_handle[3]], [atl06_handle[4],atl06_handle[5]]])

    if hold is 'off':
        show(p)
    else:
        return atl06_handle

def plot_photon_channel_distributions(h):

    beam_names = ['gt1l','gt1r','gt2l','gt2r','gt3l','gt3r']
    output_file("channel_level_photon_distribution.html", title="Channel level photon distribution")

    hist = figure(plot_width = 750,plot_height = 750,title= "purple = p1, blue = p2, red = p3, dark colors = strong, light colors = weak")

    for beam_name in beam_names:
        num_segs = np.max(h[beam_name]['segment_id']) - np.min(h[beam_name]['segment_id'])
        hist_ph, edges_ph = np.histogram(h[beam_name]['ph_id_channel'],bins=240,range=(0.5,240.5))

        if beam_name[2] is '1':
            if beam_name[3] is 'l':
                hist.quad(top=hist_ph/(len(set(h[beam_name]['segment_id']))),bottom=0,left=edges_ph[:-1],right=edges_ph[1:], fill_color="#9b59b6", line_color="#9b59b6")
            hist.quad(top=hist_ph/(len(set(h[beam_name]['segment_id']))),bottom=0,left=edges_ph[:-1],right=edges_ph[1:], fill_color="#9b59b6", line_color="#9b59b6",alpha=0.2)
        if beam_name[2] is '2':
            if beam_name[3] is 'l':
                hist.quad(top=hist_ph/(len(set(h[beam_name]['segment_id']))),bottom=0,left=edges_ph[:-1],right=edges_ph[1:], fill_color="#3498db", line_color="#3498db")
            hist.quad(top=hist_ph/(len(set(h[beam_name]['segment_id']))),bottom=0,left=edges_ph[:-1],right=edges_ph[1:], fill_color="#3498db", line_color="#3498db",alpha=0.2)
        if beam_name[2] is '3':
            if beam_name[3] is 'l':
                hist.quad(top=hist_ph/(len(set(h[beam_name]['segment_id']))),bottom=0,left=edges_ph[:-1],right=edges_ph[1:], fill_color="#e74c3c", line_color="#e74c3c")
            hist.quad(top=hist_ph/(len(set(h[beam_name]['segment_id']))),bottom=0,left=edges_ph[:-1],right=edges_ph[1:], fill_color="#e74c3c", line_color="#e74c3c",alpha=0.2)
    hist.xaxis.axis_label = 'ph_id_channel'
    hist.yaxis.axis_label = 'counts per segment'
    show(hist)

class nested_dict(dict):
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value
