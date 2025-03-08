import os,sys

def crop_around_postion( image2d_v, pos, row_width, col_width, histname ):
    from ROOT import std
    from ublarcvapp import ublarcvapp
    from larcv import larcv
    larcv.load_pyutil()

    imgutils = ublarcvapp.mctools.MCPos2ImageUtils.Get()
    imgcoord = imgutils.to_imagepos( pos[0], pos[1], pos[2], 0 )

    hist_v = []
    newmeta_v = []
    for p in range(image2d_v.size()):
        img = image2d_v.at(p)
        meta = img.meta()
        origin_wire = imgcoord[p]
        origin_tick = imgcoord[3]
        row = meta.row(origin_wire)
        col = meta.col(origin_tick)
        origin_row = max(row-int(row_width/2),0)
        origin_col = max(col-int(col_width/2),0)
        max_row = min( origin_row + row_width, meta.rows() )
        max_col = min( origin_col + col_width, meta.cols() )

        img_np = larcv.as_ndarray( img )
        img_crop_np = img_np[origin_row:max_row,origin_col:max_col]

        # new meta
        new_meta = larcv.ImageMeta( img_crop.shape[0]*meta.pixel_width(), 
            img_crop.shape[1]*meta.pixel_height(),
            max_row-origin_row, max_col-origin_col, 
            meta.tick( origin_row ), meta.wire(origin_col). meta.id() )

        # use TH2D histogram for making pictures
        img_crop = larcv.as_image2d_meta( img_crop_np, new_meta )
        hist_crop = larcv.as_th2d( img_crop, histname )
        hist_v.append( hist_crop )
        newmeta_v.append( new_meta )

    return hist_v, {'meta':newmeta_v}



