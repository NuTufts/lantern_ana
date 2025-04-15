import os,sys

def crop_around_postion( image2d_v, pos, row_width, col_width, histname ):
    from ROOT import std
    from ublarcvapp import ublarcvapp
    from larcv import larcv
    import numpy as np
    
    larcv.load_pyutil()

    imgutils = ublarcvapp.mctools.MCPos2ImageUtils.Get()
    imgcoord = imgutils.to_imagepos( pos[0], pos[1], pos[2], 0 )

    hist_v = []
    newmeta_v = []
    np_crops_v = []
    for p in range(image2d_v.size()):
        img = image2d_v.at(p)
        meta = img.meta()
        origin_wire = imgcoord[p]
        origin_tick = imgcoord[3]
        row = meta.row(origin_tick)
        col = meta.col(origin_wire)
        origin_row = max(row-int(row_width/2),0)
        origin_col = max(col-int(col_width/2),0)
        max_row = min( origin_row + row_width, meta.rows() )
        max_col = min( origin_col + col_width, meta.cols() )

        ncol = max_col-origin_col
        nrow = max_row-origin_row
        if ncol<col_width:
            origin_col = max(max_col-col_width,0)
        if nrow<row_width:
            origin_row = max(max_row-row_width,0)
        ncol = max_col-origin_col
        nrow = max_row-origin_row
        print(origin_col,max_col,ncol)
        print(origin_row,max_row,nrow)

        img_np = np.transpose( larcv.as_ndarray( img ), (1,0) )
        print("original: ",img_np.shape)
        img_crop_np = np.transpose( img_np[origin_row:max_row,origin_col:max_col], (1,0) )
        print("cropped: ",img_crop_np.shape)
        
        # new meta
        new_meta = larcv.ImageMeta( img_crop_np.shape[0]*meta.pixel_width(), 
            img_crop_np.shape[1]*meta.pixel_height(),
            nrow, ncol, 
            meta.pos_y( origin_row ), meta.pos_x(origin_col), meta.id() )
        print(new_meta.dump())
        
        # use TH2D histogram for making pictures
        img_crop = larcv.as_image2d_meta( img_crop_np, new_meta )
        hist_crop = larcv.rootutils.as_th2d( img_crop, histname+"_plane%d"%(p) )
        np_crops_v.append( img_crop_np )
        hist_v.append( hist_crop )
        newmeta_v.append( new_meta )

    return hist_v, {'meta':newmeta_v,"npimg":np_crops_v}



