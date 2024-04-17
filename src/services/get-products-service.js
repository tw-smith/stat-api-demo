import { setProductsData } from "../redux/slices/mainSlice"
import { store } from '../redux/store'


// TODO: Replace with correct endpoint in the future 
export async function GetProductsService() {

    // const allProductRequests = ALL_PROVIDERS.map(async provider => {
    //     return fetch('/api/products', {
    //         headers: new Headers({
    //             'Backend': provider.id,
    //             'Authorization': `Bearer ${userToken}`
    //         })
    //     })
    //         .then(async res => await res.json())
    //         .then(data => { return { 'provider': provider.id, 'data': data } })
    // });

    // Promise.all(allProductRequests).then((results) => {
    //     store.dispatch(setProductsData(Object.fromEntries(Object.values(results).map(value => {
    //         return value.data.products
    //     }))))
    // }).catch(e => setError(e));


    const eusiProducts =
        [
            {
                "type": "Product",
                "stat_version": "0.0.1",
                "stat_extensions": [],
                "id": "maxar_opt",
                "title": "Maxar tasking",
                "description": "",
                "keywords": [
                    "EO",
                    "OPTICAL",
                    "WV01",
                    "WV02",
                    "WV03",
                    "GE01",
                    "VHR"
                ],
                "license": "proprietary",
                "providers": [
                    {
                        "name": "EUSI",
                        "description": null,
                        "roles": [
                            "licensor",
                            "processor",
                            "producer",
                            "host"
                        ],
                        "url": "https://www.euspaceimaging.com"
                    }
                ],
                "links": [],
                "constraints": {
                    "taskingScheme": {
                        "description": "Property containing the type of tasking scheme to apply to the subOrder",
                        "type": "string",
                        "enum": [
                            "single_window"
                        ],
                        "default": "single_window"
                    },
                    "taskingPriority": {
                        "description": "Property containing the tasking priority level to apply to the subOrder",
                        "type": "string",
                        "enum": [
                            "Select",
                            "Select Plus"
                        ],
                        "default": "Select"
                    },
                    "maxCloudCover": {
                        "minimum": 5.0,
                        "maximum": 100.0
                    },
                    "minOffNadir": {
                        "minimum": 0.0,
                        "maximum": 15.0
                    },
                    "maxOffNadir": {
                        "minimum": 10.0,
                        "maximum": 45.0
                    },
                    "scanDirection": {
                        "description": "Property describing the allowed scan direction value to apply to the subOrder",
                        "type": "string",
                        "enum": [
                            "Any"
                        ]
                    },
                    "singleSensor": {
                        "description": "Property forcing collection of the area of interest with a single sensor",
                        "type": "boolean",
                        "default": false
                    },
                    "sensors": {
                        "description": "Array containing the values of the allowed sensors for imagery collection",
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": [
                                "WV01",
                                "WV02",
                                "WV03",
                                "GE01"
                            ]
                        }
                    },
                    "stereo": {
                        "description": "Property describing whether to collect this subOrder as in-track stereo",
                        "type": "boolean",
                        "default": false
                    },
                    "required": [
                        "taskingScheme",
                        "maxCloudCover",
                        "maxOffNadir",
                        "stereo",
                        "sensors",
                        "taskingPriority"
                    ]
                },
                "parameters": {
                    "customerReference": {
                        "title": "Customer Reference",
                        "description": "Free text parameter containing the client reference to the overall order",
                        "type": "string"
                    },
                    "purchaseOrderNo": {
                        "title": "Purchase Order Number",
                        "description": "Free text parameter containing the a client-side purchase order number to apply to the invoice",
                        "type": "string"
                    },
                    "projectName": {
                        "title": "Project Name",
                        "description": "Free text parameter containing a client-side reference to an overarching project",
                        "type": "string"
                    },
                    "productLevel": {
                        "title": "Product Level",
                        "description": "Property containing the production level to apply to delivered product",
                        "type": "string",
                        "enum": [
                            "OR2A",
                            "ORTHO",
                            "2A"
                        ],
                        "default": "OR2A"
                    },
                    "bandCombination": {
                        "title": "Band combination",
                        "description": "Property containing the band combination to apply to delivered product",
                        "type": "string",
                        "enum": [
                            "PAN",
                            "4PS",
                            "4BB",
                            "8BB"
                        ],
                        "default": "4BB"
                    },
                    "resolution": {
                        "title": "Resolution",
                        "description": "Property containing the resolution apply to delivered product",
                        "type": "number",
                        "enum": [
                            0.5,
                            0.4,
                            0.3
                        ],
                        "default": 0.5
                    },
                    "bitDepth": {
                        "title": "Bit depth",
                        "description": "Property containing the bit depth to apply to delivered product",
                        "type": "integer",
                        "enum": [
                            8,
                            11,
                            16
                        ],
                        "default": 16
                    },
                    "resamplingKernel": {
                        "title": "Resampling Kernel",
                        "description": "Property containing the resampling kernel to apply to delivered product",
                        "type": "string",
                        "enum": [
                            "NN",
                            "MTF",
                            "CC",
                            "PS",
                            "ENH"
                        ],
                        "default": "CC"
                    },
                    "dra": {
                        "title": "DRA",
                        "description": "Property describing whether to apply dynamic range adjustment to delivered product",
                        "type": "boolean",
                        "default": false
                    },
                    "acomp": {
                        "title": "ACOMP",
                        "description": "Property describing whether to apply atmospheric compensation to delivered product",
                        "type": "boolean",
                        "default": false
                    },
                    "format": {
                        "title": "Format",
                        "description": "Property containing the final product format to apply to delivered product",
                        "type": "string",
                        "enum": [
                            "GeoTIFF"
                        ],
                        "default": "GeoTIFF"
                    },
                    "fullStrip": {
                        "type": "boolean",
                        "default": false
                    },
                    "projection": {
                        "title": "Product projection",
                        "description": "Property containing the projection to apply to delivered product",
                        "type": "string",
                        "enum": [
                            "UTM_WGS84_Meter",
                            "Geographic_WGS84_DecimalDegree"
                        ]
                    },
                    "priority": {
                        "title": "Production priority",
                        "description": "Property containing the priority class of the order",
                        "type": "string",
                        "enum": [
                            "Standard"
                        ]
                    },
                    "required": [
                        "productLevel",
                        "bandCombination",
                        "resolution",
                        "priority"
                    ]
                }
            }
        ]

    const planetProducts = [
        {
            "type": "Product",
            "stat_version": "stat_version",
            "stat_extensions": [],
            "id": "PL-QA:Assured Tasking",
            "title": "Assured Tasking",
            "description": "An assured capture at a specific time and location.",
            "keywords": ["EO", "color"],
            "license": "Planet",
            "providers": {
                "name": "planet",
                "description": "planet description",
                "roles": ["producer"],
                "url": "planet link"
            },
            "links": [{
                "href": "https://example.com/",
                "rel": "latest-version",
                "type": "media type",
                "title": "title"
            }],
            "constraints": {
                "allowed_geometry": ["Point", "LineString"],
                "max_aoi_size_sqkm": 500,
                "comment_max_aoi_size_sqkm": "this does not correspond to a value the customer would send, but to a property of the provided AOI that we'll validate",
                "scheduling_type": "Assured",
                "comment_scheduling_type": "not a choice but using the constraints field to persist the product type",
                "satellite_types": ["SkySat"],
            },
            "parameters": {
                "exclusivity_days": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 30
                }
            },
            "properties": {}
        },
        {
            "type": "Product",
            "stat_version": "stat_version",
            "stat_extensions": [],
            "id": "PL-QA:Flexible Tasking",
            "title": "Flexible Tasking",
            "description": "An order to take a capture over a period of time.",
            "keywords": ["EO", "color"],
            "license": "Planet",
            "providers": {
                "name": "planet",
                "description": "planet description",
                "roles": ["producer"],
                "url": "planet link"
            },
            "links": [{
                "href": "https://example.com/",
                "rel": "latest-version",
                "type": "media type",
                "title": "title"
            }],
            "constraints": {
                "allowed_geometry": ["Point", "LineString", "Polygon"],
                "max_aoi_size_sqkm": 500,
                "scheduling_type": "Flexible",
                "satellite_types": ["SkySat"],
                "duration": {
                    "type": "timedelta",
                    "minimum": "1d",
                    "maximum": "364d,23h,59m,59s"
                },

                "view:sat_elevation": {
                    "type": "number",
                    "min": 20,
                    "max": 90
                },
                "view:azimuth": {
                    "type": "number",
                    "min": -360,
                    "max": 360
                },
                "view:sun_zenith": {
                    "type": "number",
                    "min": 0,
                    "max": 85
                },
                "view:sun-azimuth": {
                    "type": "number",
                    "min": -360,
                    "max": 360
                }
            },
            "parameters": {
                "exclusivity_days": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 30
                }
            },
            "properties": {}
        }
    ]

    const umbraProducts = [
        {
            "type": "Product",
            "stat_version": "stat_version",
            "stat_extensions": [
                "product_extention_schema_link_1",
                "product_extention_schema_link_2"
            ],
            "id": "umbra_spotlight",
            "title": "Umbra Spotlight",
            "description": "Spotlight images served from the Archive or by creating new Orders. Way more detail here or a link down in links to Product documentation.",
            "keywords": [
                "SAR",
                ""
            ],
            "license": "license",
            "providers": {
                "name": "umbra",
                "description": "umbra description",
                "roles": [
                    "producer"
                ],
                "url": "umbra link"
            },
            "links": {
                "href": "https://example.com/",
                "rel": "latest-version",
                "type": "media type",
                "title": "title"
            },
            "constraints": {
                "$defs": {
                    "SceneSize": {
                        "enum": [
                            "5x5_KM",
                            "10x10_KM"
                        ],
                        "title": "SceneSize",
                        "type": "string"
                    }
                },
                "description": "Umbra Spotlight OpportunityConstraints docstring yay!",
                "properties": {
                    "windowStartAt": {
                        "description": "windowStartAt must be a ISO8601 string and be before windowEndAt. If this field is in the past, Umbra's Archive Catalog may be used to satisfy the Opportunity.",
                        "format": "date-time",
                        "title": "Windowstartat",
                        "type": "string"
                    },
                    "windowEndAt": {
                        "description": "windowEndAt must be a ISO8601 string and be after windowStartAt. If this field is in the past, Umbra's Archive Catalog will be used to satisfy the Opportunity.",
                        "format": "date-time",
                        "title": "Windowendat",
                        "type": "string"
                    },
                    "sceneSize": {
                        "allOf": [
                            {
                                "$ref": "#/$defs/SceneSize"
                            }
                        ],
                        "default": "5x5_KM",
                        "description": "The scene size of the Spotlight collect. The first "
                    },
                    "grazingAngleMinDegrees": {
                        "default": 10,
                        "description": "The minimum angle between the local tangent plane at the target location and the line of sight vector between the satellite and the target.",
                        "minimum": 10,
                        "title": "Grazinganglemindegrees",
                        "type": "integer"
                    },
                    "grazingAngleMaxDegrees": {
                        "default": 80,
                        "description": "The maximum angle between the local tangent plane at the target location and the line of sight vector between the satellite and the target.",
                        "maximum": 80,
                        "title": "Grazinganglemaxdegrees",
                        "type": "integer"
                    },
                    "satelliteIds": {
                        "description": "The satellites to consider for this Opportunity. ",
                        "items": {
                            "type": "string",
                            "regex": "Umbra-\\d{2}"
                        },
                        "title": "Satelliteids",
                        "type": "array"
                    }
                },
                "required": [
                    "windowStartAt",
                    "windowEndAt",
                    "satelliteIds"
                ],
                "title": "UmbraSpotlightOpportunityConstraints",
                "type": "object"
            },
            "parameters": {
                "$defs": {
                    "ProductType": {
                        "enum": [
                            "GEC",
                            "SIDD"
                        ],
                        "title": "ProductType",
                        "type": "string"
                    }
                },
                "properties": {
                    "deliveryConfigId": {
                        "anyOf": [
                            {
                                "format": "uuid",
                                "type": "string"
                            },
                            {
                                "type": "null"
                            }
                        ],
                        "default": null,
                        "description": "",
                        "title": "Deliveryconfigid"
                    },
                    "productTypes": {
                        "default": [
                            "GEC"
                        ],
                        "description": "",
                        "items": {
                            "$ref": "#/$defs/ProductType"
                        },
                        "title": "Producttypes",
                        "type": "array"
                    }
                },
                "title": "UmbraSpotlightOrderParameters",
                "type": "object"
            }
        }
    ]


    store.dispatch(setProductsData([...eusiProducts, ...umbraProducts, ...planetProducts]))

}
