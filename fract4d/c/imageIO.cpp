#include <stdlib.h>
#include <stdio.h>

#include "image_public.h"

class image_writer : public ImageWriter
{
public:
    virtual ~image_writer() {};
protected:
    image_writer(FILE *fp_, IImage *image_) {
        fp = fp_;
        im = image_;
    }

    FILE *fp;
    IImage *im;
};

class image_reader : public ImageReader
{
public:
    virtual ~image_reader() {};
protected:
    image_reader(FILE *fp_, IImage *image_) {
        fp = fp_;
        im = image_;
    }

    FILE *fp;
    IImage *im;
};

#ifdef PNG_ENABLED
extern "C" {
#include "png.h"
}

class png_writer : public image_writer 
{
public:
    png_writer(FILE *fp, IImage *image) : image_writer(fp,image) {
        ok = false;
        png_ptr = png_create_write_struct(
            PNG_LIBPNG_VER_STRING,
            NULL, NULL, NULL); // FIXME do more error handling

        if(NULL == png_ptr)
        {
            return;
        }

        info_ptr = png_create_info_struct(png_ptr);
        if(NULL == info_ptr)
        {
            png_destroy_write_struct(&png_ptr, (png_infopp)NULL);
            return;
        }

        if (setjmp(png_jmpbuf(png_ptr)))
        {
            /* If we get here, we had a problem writing the file */
            png_destroy_write_struct(&png_ptr, &info_ptr);
            return;
        }

        png_init_io(png_ptr, fp);

        ok = true;
    };
    ~png_writer() {
        if(ok)
        {
            png_destroy_write_struct(&png_ptr, &info_ptr);
        }
    }

    bool save_header();
    bool save_tile();
    bool save_footer();

private:
    bool ok;
    png_structp png_ptr;
    png_infop info_ptr;
};

bool
png_writer::save_header()
{
    png_set_IHDR(
        png_ptr, info_ptr, 
        im->totalXres(), im->totalYres(), // width, height
        8, PNG_COLOR_TYPE_RGB, // bit depth, color type
        PNG_INTERLACE_NONE, 
        PNG_COMPRESSION_TYPE_BASE, PNG_FILTER_TYPE_BASE);
    
    png_write_info(png_ptr, info_ptr);

    return true;
}

bool 
png_writer::save_tile()
{
    for (int y = 0; y < im->Yres(); y++)
    {
        png_bytep row = (png_bytep)(im->getBuffer() + im->row_length() * y); 
        png_write_rows(png_ptr, &row, 1);
    }
    return true;
}

bool
png_writer::save_footer()
{
   png_write_end(png_ptr, info_ptr);
   return true;
}

#endif

ImageWriter *
ImageWriter::create(image_file_t file_type, FILE *fp, IImage *image)
{
    switch(file_type)
    {
    case FILE_TYPE_TGA:
        //return new tga_writer(fp, image);
    case FILE_TYPE_PNG:
      #ifdef PNG_ENABLED
        return new png_writer(fp, image);
      #endif
        break;
    case FILE_TYPE_JPG:
      #ifdef JPG_ENABLED
        //return new jpg_writer(fp, image);
      #endif
        break;
    }
    return NULL; // unknown file type
}


