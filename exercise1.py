import arcpy
import os
import sys
import logging

logger = logging.getLogger(__name__)


def setup_logging(level='INFO'):
    r"""Configures the logger Level.
    Arguments:
        level: CRITICAL -> ERROR -> WARNING -> INFO -> DEBUG.
    Side effect:
        The minimum logging level is set.
    """
    ll = logging.getLevelName(level)
    logger = logging.getLogger()
    logger.handlers.clear()
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s %(name)-12s %(levelname)-8s"
        "{'file': %(filename)s 'function': %(funcName)s 'line': %(lineno)s}\n"
        "message: %(message)s\n")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(ll)

def pwd():
    wd = sys.path[0]
    logger.info('wd: {0}'.format(wd))
    return wd

def set_path(wd, data_path):
    path_name = os.path.join(wd, data_path)
    logger.info('path_name: {0}'.format(path_name))
    return path_name

def import_spatial_reference(dataset):
    spatial_reference = arcpy.Describe(dataset).SpatialReference
    logger.info('spatial_reference: {0}'.format(spatial_reference.name))
    return spatial_reference


def setup_env(workspace_path, spatial_ref_dataset):
    # Set workspace path.
    arcpy.env.workspace = workspace_path
    logger.info('workspace(s): {}'.format(arcpy.env.workspace))

    # Set output overwrite option.
    arcpy.env.overwriteOutput = True
    logger.info('overwriteOutput: {}'.format(arcpy.env.overwriteOutput))

    # Set the output spatial reference.
    arcpy.env.outputCoordinateSystem = import_spatial_reference(
        spatial_ref_dataset)
    logger.info('outputCoordinateSystem: {}'.format(
        arcpy.env.outputCoordinateSystem.name))


def count_selected(fc):
    # Side effect is: message printed with the count of selected features.
    f_count = arcpy.management.GetCount(fc)
    print('Current Selected from {0}: {1}'.format(fc, f_count))


def clear_selected(fc):
    # Side effect is: selected features are cleared.
    # count_selected is called for verification.
    arcpy.management.SelectLayerByAttribute(fc, "CLEAR_SELECTION")
    count_selected(fc)

def run_model(spatial_ref_dataset, ll='INFO'):
    setup_logging(ll)
    # Assumes that this module is in the ArcGIS Pro project directory.
    # pwd() should be the
    wd = pwd()
    input_db = set_path(wd, 'gis305-test.gdb')
    output_db = set_path(wd, 'gis305-test-outputs.gdb')
    logger.info('output db: {0}'.format(output_db))
    setup_env(input_db, spatial_ref_dataset)

    arcpy.SelectLayerByAttribute_management("cities", "CLEAR_SELECTION")

    flayer = arcpy.MakeFeatureLayer_management("cities", "Cities_Layer")

    qry = "POP1990 > 20000"
    arcpy.management.SelectLayerByAttribute(flayer, "NEW_SELECTION", qry)

    my_cnt = arcpy.management.GetCount(flayer)
    print(f"Selected cities is: {my_cnt}")

    arcpy.management.SelectLayerByLocation(flayer, "WITHIN_A_DISTANCE", "us_rivers", "10 miles", "SUBSET_SELECTION")

    my_cnt = arcpy.management.GetCount(flayer)
    print(f"Selected cities is: {my_cnt}")

    # flayer = arcpy.MakeFeatureLayer_management("cities", "Cities_Layer")
    field = 'POP1990'
    total = 0
    i = 1
    with arcpy.da.SearchCursor(flayer, field) as cursor:
        for row in cursor:
            print(i, str(row[0]))
            total = total + row[0]
            i = i + 1

    print(f"Total population is: {total:,}")

if __name__ == '__main__':
    run_model('cities')