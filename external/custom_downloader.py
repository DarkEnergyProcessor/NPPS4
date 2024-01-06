# NPPS4 example custom download backend provider.
# This file define list of functions that must be implemented for custom download
# backend provider. If in doubt, it's probably easier for you to use existing
# download backend specified in the configuration files.
#
# Please read the comments on how to implement your own custom download backend provider.
#
# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or distribute
# this software, either in source code form or as a compiled binary, for any
# purpose, commercial or non-commercial, and by any means.
#
# In jurisdictions that recognize copyright laws, the author or authors of this
# software dedicate any and all copyright interest in the software to the public
# domain. We make this dedication for the benefit of the public at large and to
# the detriment of our heirs and successors. We intend this dedication to be an
# overt act of relinquishment in perpetuity of all present and future rights to
# this software under copyright law.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# For more information, please refer to <http://unlicense.org/>

import npps4.idoltype
import npps4.download.dltype

import fastapi


# This is place to initialize your custom downloader backend when it's being used.
def initialize():
    pass


# Please return the latest LL!SIF server version.
def get_server_version() -> str:
    return "59.4"


# Please return absolute path to the decrypted client SQLite3 databases.
# Parameters:
# * "name" (str) - Name of the client database to retrieve.
def get_db_path(name: str) -> str:
    # For example, if the "name" is "live", then it's looking for decrypted
    # client live.db_ SQLite3 database file.
    raise NotImplementedError(f"Not implemented get_db_path('{name}')")


# This function return list of files that client must download before being updated to latest server version specified
# in get_server_info() function. Please see npps4.download.dltype.UpdateInfo structure on how to return the URLs.
# Parameters:
# * "request" (fastapi.Request) - The FastAPI request object
# * "platform" (npps4.idoltype.PlatformType) - Client platform. This can be iOS (1) or Android (2).
# * "from_client_version" (tuple of 2 ints) - Current client version, specified as (major, minor).
async def get_update_files(
    request: fastapi.Request, platform: npps4.idoltype.PlatformType, from_client_version: tuple[int, int]
) -> list[npps4.download.dltype.UpdateInfo]:
    raise NotImplementedError(f"not implemented get_update_files(FastAPI, {platform}, '{from_client_version}')")


# This function return list of files that client has to download when batch-downloading files.
# Parameters:
# * "request" (fastapi.Request) - The FastAPI request object
# * "platform" (npps4.idoltype.PlatformType) - Client platform. This can be iOS (1) or Android (2).
# * "package_type" (int) - Package type to download. Possible values are between 0 and 6 inclusive.
# * "exclude" (list of ints) - List of package ID respective to the package type to exclude from download. This means
#                              the client already have these package IDs.
async def get_batch_files(
    request: fastapi.Request, platform: npps4.idoltype.PlatformType, package_type: int, exclude: list[int]
) -> list[npps4.download.dltype.BatchInfo]:
    raise NotImplementedError(f"not implemented get_batch_files(FastAPI, {platform}, {package_type}, {repr(exclude)})")


# This function return list of files that client has to download when downloading a single package.
# Parameters:
# * "request" (fastapi.Request) - The FastAPI request object
# * "platform" (npps4.idoltype.PlatformType) - Client platform. This can be iOS (1) or Android (2).
# * "package_type" (int) - Package type to download. Possible values are between 0 and 6 inclusive.
# * "package_id" (int) -Package ID respective to the package type to download.
async def get_single_package(
    request: fastapi.Request, platform: npps4.idoltype.PlatformType, package_type: int, package_id: int
) -> list[npps4.download.dltype.BaseInfo] | None:
    raise NotImplementedError(f"not implemented get_single_package(FastAPI, {platform}, {package_type}, {package_id})")


# This function return list of files that client has to download when downloading a single file through micro download
# functionality (as in "Light Download Mode").
# Parameters:
# * "request" (fastapi.Request) - The FastAPI request object
# * "platform" (npps4.idoltype.PlatformType) - Client platform. This can be iOS (1) or Android (2).
# * "files" (list of strs) - List of files that client requested, relative to their "external" folder. If a file does
#                            not exist, this function must still return valid-but-404 URLs.
async def get_raw_files(
    request: fastapi.Request, platform: npps4.idoltype.PlatformType, files: list[str]
) -> list[npps4.download.dltype.BaseInfo]:
    raise NotImplementedError(f"not implemented get_raw_files(FastAPI, {platform}, {repr(files)})")
