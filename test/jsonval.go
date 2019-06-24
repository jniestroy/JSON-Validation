package main

import (
	"encoding/json"
	"fmt"

	"github.com/qri-io/jsonschema"
)

func main() {
	var schemaData = []byte(` {
		"definitions": {},
		"$schema": "http://json-schema.org/draft-07/schema#",
		"$id": "http://example.com/root.json",
		"type": "object",
		"title": "The Root Schema",
		"required": [
		  "@context",
		  "@type",
		  "name",
		  "description",
		  "url",
		  "identifier",
		  "keywords",
		  "creator"
 ],
	  "properties": {
		 "@context": {
		   "$id": "#/properties/@context",
		   "type": "string",
		   "title": "The @context Schema",
		   "default": "",
		   "examples": [
			 "https://schema.org/"
		   ],
		   "pattern": "^(.*)$"
		 },
		 "@type": {
		   "$id": "#/properties/@type",
		   "type": "string",
		   "title": "The @type Schema",
		   "default": "",
		   "examples": [
			 "Dataset"
		   ],
		   "pattern": "^(.*)$"
		 },
		 "name": {
		   "$id": "#/properties/name",
		   "type": "string",
		   "title": "The Name Schema",
		   "default": "",
		   "examples": [
			 "NCDC Storm Events Database"
		   ],
		   "pattern": "^(.*)$"
		 },
		 "description": {
		   "$id": "#/properties/description",
		   "type": "string",
		   "title": "The Description Schema",
		   "default": "",
		   "examples": [
			 "Storm Data is provided by the National Weather Service (NWS) and contain statistics on..."
		   ],
		   "pattern": "^(.*)$"
		 },
		 "url": {
		   "$id": "#/properties/url",
		   "type": "string",
		   "title": "The Url Schema",
		   "default": "",
		   "examples": [
			 "https://catalog.data.gov/dataset/ncdc-storm-events-database"
		   ],
		   "pattern": "^(.*)$"
		 },
		 "identifier": {
		   "$id": "#/properties/identifier",
		   "type": "array",
		   "title": "The Identifier Schema",
		   "items": {
			 "$id": "#/properties/identifier/items",
			 "type": "string",
			 "title": "The Items Schema",
			 "default": "",
			 "examples": [
			   "https://doi.org/10.1000/182",
			   "https://identifiers.org/ark:/12345/fk1234"
			 ],
			 "pattern": "^(.*)$"
		   }
		 },
		 "keywords": {
		   "$id": "#/properties/keywords",
		   "type": "array",
		   "title": "The Keywords Schema",
		   "items": {
			"$id": "#/properties/keywords/items",
			"type": "string",
			"title": "The Items Schema",
		   "default": "",
			"examples": [
			  "ATMOSPHERE > ATMOSPHERIC PHENOMENA > CYCLONES",
			  "ATMOSPHERE > ATMOSPHERIC PHENOMENA > DROUGHT",
			  "ATMOSPHERE > ATMOSPHERIC PHENOMENA > FOG",
			  "ATMOSPHERE > ATMOSPHERIC PHENOMENA > FREEZE"
			],
			"pattern": "^(.*)$"
		  }
		},
		"creator": {
		  "$id": "#/properties/creator",
		  "type": "object",
		  "title": "The Creator Schema",
		  "required": [
			"@type",
			"name"
		  ],
		  "properties": {
			"@type": {
			  "$id": "#/properties/creator/properties/@type",
			  "type": "string",
			  "title": "The @type Schema",
			  "default": "",
			  "examples": [
				"Organization"
			  ],
			  "pattern": "^(.*)$"
			},
			"url": {
			  "$id": "#/properties/creator/properties/url",
			  "type": "string",
			  "title": "The Url Schema",
			  "default": "",
			  "examples": [
				"https://www.ncei.noaa.gov/"
			  ],
			  "pattern": "^(.*)$"
			},
			"name": {
			  "$id": "#/properties/creator/properties/name",
			  "type": "string",
			  "title": "The Name Schema",
			  "default": "",
			  "examples": [
				"OC/NOAA/NESDIS/NCEI > National Centers for Environmental Information, NESDIS, NOAA, U.S. Department of Commerce"
			  ],
			  "pattern": "^(.*)$"
			},
			"contactPoint": {
			  "$id": "#/properties/creator/properties/contactPoint",
			  "type": "object",
			  "title": "The Contactpoint Schema",
			  "required": [
				"@type",
				"contactType",
				"telephone",
				"email"
			  ],
			  "properties": {
				"@type": {
				  "$id": "#/properties/creator/properties/contactPoint/properties/@type",
				  "type": "string",
				  "title": "The @type Schema",
				  "default": "",
				  "examples": [
				   "ContactPoint"
				  ],
				  "pattern": "^(.*)$"
				},
				"contactType": {
				  "$id": "#/properties/creator/properties/contactPoint/properties/contactType",
				  "type": "string",
				 "title": "The Contacttype Schema",
				  "default": "",
				  "examples": [
					"customer service"
				  ],
				  "pattern": "^(.*)$"
				},
				"telephone": {
				  "$id": "#/properties/creator/properties/contactPoint/properties/telephone",
				  "type": "string",
				  "title": "The Telephone Schema",
				  "default": "",
				  "examples": [
					"+1-828-271-4800"
				  ],
				  "pattern": "^(.*)$"
				},
				"email": {
				  "$id": "#/properties/creator/properties/contactPoint/properties/email",
				  "type": "string",
				  "title": "The Email Schema",
				  "default": "",
				  "examples": [
					"ncei.orders@noaa.gov"
				  ],
				  "pattern": "^(.*)$"
			 }
			}
		  }
		}
	  }
	}
 }`)

	rs := &jsonschema.RootSchema{}
	if err := json.Unmarshal(schemaData, rs); err != nil {
		panic("unmarshal schema: " + err.Error())
	}

	var validData = []byte(`{
		"@context":"https://schema.org/",
		"@type":"Dataset",
		"name":"NCDC Storm Events Database",
		"description":"Storm Data is provided by the National Weather Service (NWS) and contain statistics on...",
		"url":"https://catalog.data.gov/dataset/ncdc-storm-events-database",
		"sameAs":"https://gis.ncdc.noaa.gov/geoportal/catalog/search/resource/details.page?id=gov.noaa.ncdc:C00510",
		"identifier": ["https://doi.org/10.1000/182",
					   "https://identifiers.org/ark:/12345/fk1234"],
		"keywords":[
		   "ATMOSPHERE > ATMOSPHERIC PHENOMENA > CYCLONES",
		   "ATMOSPHERE > ATMOSPHERIC PHENOMENA > DROUGHT",
		   "ATMOSPHERE > ATMOSPHERIC PHENOMENA > FOG",
		   "ATMOSPHERE > ATMOSPHERIC PHENOMENA > FREEZE"
		],
		"creator":{
		   "@type":"Organization",
		   "url": "https://www.ncei.noaa.gov/",
		   "name":"OC/NOAA/NESDIS/NCEI > National Centers for Environmental Information, NESDIS, NOAA, U.S. Department of Commerce",
		   "contactPoint":{
			  "@type":"ContactPoint",
			  "contactType": "customer service",
			  "telephone":"+1-828-271-4800",
			  "email":"ncei.orders@noaa.gov"
		   }
		},
		"includedInDataCatalog":{
		   "@type":"DataCatalog",
		   "name":"data.gov"
		},
		"distribution":[
		   {
			  "@type":"DataDownload",
			  "encodingFormat":"CSV",
			  "contentUrl":"http://www.ncdc.noaa.gov/stormevents/ftp.jsp"
		   },
		   {
			  "@type":"DataDownload",
			  "encodingFormat":"XML",
			  "contentUrl":"http://gis.ncdc.noaa.gov/all-records/catalog/search/resource/details.page?id=gov.noaa.ncdc:C00510"
		   }
		],
		"temporalCoverage":"1950-01-01/2013-12-18",
		"spatialCoverage":{
		   "@type":"Place",
		   "geo":{
			  "@type":"GeoShape",
			  "box":"18.0 -65.0 72.0 172.0"
		   }
		}
	}`)
	if errors, _ := rs.ValidateBytes(validData); len(errors) > 0 {
		fmt.Println(errors[0].Error())
	} else {
		fmt.Println("Correctly Validated Data")
	}
	testjson := map[string]interface{}{
		"@context":    "https://schema.org/",
		"@type":       "Dataset",
		"name":        "NCDC Storm Events Database",
		"description": "Storm Data is provided by the National Weather Service (NWS) and contain statistics on...",
		"url":         "https://catalog.data.gov/dataset/ncdc-storm-events-database",
		"sameAs":      "https://gis.ncdc.noaa.gov/geoportal/catalog/search/resource/details.page?id=gov.noaa.ncdc:C00510",
		"identifier": []string{"https://doi.org/10.1000/182",
			"https://identifiers.org/ark:/12345/fk1234"},
		"keywords": []string{
			"ATMOSPHERE > ATMOSPHERIC PHENOMENA > CYCLONES",
			"ATMOSPHERE > ATMOSPHERIC PHENOMENA > DROUGHT",
			"ATMOSPHERE > ATMOSPHERIC PHENOMENA > FOG",
			"ATMOSPHERE > ATMOSPHERIC PHENOMENA > FREEZE",
		},
		"creator": map[string]interface{}{
			"@type": "Organization",
			"url":   "https://www.ncei.noaa.gov/",
			"name":  "OC/NOAA/NESDIS/NCEI > National Centers for Environmental Information, NESDIS, NOAA, U.S. Department of Commerce",
			"contactPoint": map[string]interface{}{
				"@type":       "ContactPoint",
				"contactType": "customer service",
				"telephone":   "+1-828-271-4800",
				"email":       "ncei.orders@noaa.gov",
			},
		},
	}
	hopedata, _ := json.Marshal(testjson)
	if errors, _ := rs.ValidateBytes(hopedata); len(errors) > 0 {
		fmt.Println(errors[0].Error())
	} else {
		fmt.Println("Correctly Validated Data")
	}

}
