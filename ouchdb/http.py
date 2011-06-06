# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""HTTP Error codes.
"""
import web
import urlparse
import json

class Created(web.HTTPError):
    def __init__(self, location, data):
        location = urlparse.urljoin(web.ctx.path, location)
        if location.startswith('/'):
            location = web.ctx.home + location
        headers = {
            "Location": location
        }
        web.HTTPError.__init__(self, '201 Created', headers=headers, data=json.dumps(data))


class NotFound(web.HTTPError):
    def __init__(self, data):
        web.HTTPError.__init__(self, '404 Object Not Found', headers={}, data=json.dumps(data))


class Conflict(web.HTTPError):
    def __init__(self, data):
        web.HTTPError.__init__(self, '409 Conflict', headers={}, data=json.dumps(data))


class PreconditionFailed(web.HTTPError):
    def __init__(self, data):
        HTTPError.__init__(self, '412 Precondition Failed', headers={}, data=json.dumps(data))
