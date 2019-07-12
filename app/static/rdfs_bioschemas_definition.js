{
  "@context": {
    "rdfs": "https://www.w3.org/TR/rdf-schema/",
    "schema": "https://schema.org/",
    "bio": "http://bioschemas.org/specifications/",
    "pending": "http://pending.schema.org/",
  },
  "@graph": [
    {"@id" : "bio:DataCatalog",
      "@type": "rdfs:Class",
      "rdfs:subClassOf": "schema:DataCatalog"
      },
    {"@id" : "bio:Dataset",
        "@type": "rdfs:Class",
        "rdfs:subClassOf": "schema:Dataset"
      },
    {"@id" : "bio:Gene",
        "@type": "rdfs:Class",
        "rdfs:subClassOf": "bio:BioChemEntity"
      },
    {"@id" : "bio:Sample",
      "@type": "rdfs:Class",
      "rdfs:label": "The data and metadata involved in the collection of data, with reference to methods and experimental design.",
      "rdfs:subClassOf": "schema:Thing"
    },
    {"@id" : "bio:Tool",
      "@type": "rdfs:Class",
      "rdfs:subClassOf": "schema:SoftwareApplication",
      "rdfs:label": "Bioschemas spec for describing a SoftwareApplication in the life sciences"
    },

    {"@id": "bio:CategoryCode",
      "@type": "rdfs:Class",
      "rdfs:label": "An extension of 'Medical Code' in the health-lifesci.schema.org for BioChemical Codes",
      "rdfs:subClassOf": "http://health-lifesci.schema.org/MedicalCode"
    },
      {"@id": "bio:name",
        "@type": "rdfs:property",
        "rdfs:label": "A human readable label",
        "rdfs:domain": "bio:CategoryCode",
        "rdfs:range": "schema:Text"
        },
      {"@id": "bio:codeValue",
        "@type": "rdfs:property",
        "rdfs:label": "A short textual code that uniquely identifies the value",
        "rdfs:domain": "bio:CategoryCode",
        "rdfs:range": "schema:Text"
        },
      {"@id": "bio:url",
        "@type": "rdfs:property",
        "rdfs:label": "The URI for the vocabulary code",
        "rdfs:domain": "bio:CategoryCode",
        "rdfs:range": "schema:URL"
        },

    {"@id": "bio:PropertyValue",
      "@type": "rdfs:Class",
      "rdfs:label": "PropertyValue recommendations specific to the bioschemas Sample class",
      "rdfs:subClassOf": "schema:PropertyValue"
    },
      {"@id": "bio:valueReference",
        "@type": "rdfs:property",
        "rdfs:label": "A pointer to a secondary value with additional information",
        "rdfs:domain": "bio:PropertyValue",
        "rdfs:range": "bio:CategoryCode"
        },
      {"@id": "bio:unitCode",
        "@type": "rdfs:property",
        "rdfs:label": "The unit of measurement given using the UN/CEFACT Common Code (3 characters) or a URL",
        "rdfs:domain": "bio:PropertyValue",
        "rdfs:range": ["schema:Text", "schema:URL"]
        },
      {"@id": "bio:unitText",
        "@type": "rdfs:property",
        "rdfs:label": "String Indicating the Unit of Measurment",
        "rdfs:domain": "bio:PropertyValue",
        "rdfs:range": "schema:Text"
        },


    {"@id": "bio:supportedRefs",
      "rdfs:label": "Supported Genome ID references",
      "@type": "rdfs:Property",
      "rdfs:domain": [
        "bio:Beacon"
      ],
      "rdfs:range": [
        "schema:Text"
      ]
    },
    {"@id": "bio:aggregator",
      "rdfs:label": "True if Beacon is an aggregator of other Beacon Datasets",
      "@type": "rdfs:Property",
      "rdfs:domain": [
        "bio:DataCatalog"
      ],
      "rdfs:range": [
        "schema:Text"
      ]
    },
    {"@id": "bio:isBasisFor",
      "@type": "rdfs:Property",
      "rdfs:domain": [
        "bio:DataRecord"
      ],
      "rdfs:range": [
        "schema:CreativeWork",
        "schema:Product",
        "schema:URL"
      ]
    },
    {"@id": "bio:seeAlso",
      "rdfs:label": "A pointer to any related entity",
      "@type": "rdfs:Property",
      "rdfs:domain": [
        "bio:DataRecord"
      ],
      "rdfs:range": [
        "schema:Thing",
        "schema:URL"
        ]
      },
    {"@id": "measurementTechnique",
      "rdfs:label": "A technique or technology used in a Dataset, corresponding to the method used for measuring the corresponding variable(s) described using variableMeasured",
      "@type": "rdfs:Property",
      "rdfs:domain": [
        "bio:Dataset"
      ],
      "rdfs:range": [
        "schema:Text",
        "schema:URL"
      ]
      },
    {"@id": "variableMeasured",
      "rdfs:label": "What does the dataset measure? (e.g. temperature, pressure)",
      "@type": "rdfs:Property",
      "rdfs:domain": [
        "bio:Dataset"
        ],
      "rdfs:range": [
        "schema:PropertyValue",
        "schema:Text"
        ]
      },
    {"@id": "bio:encodes",
      "rdfs:label": "Property links gene products encoded directly or indirectly, from a gene such as RNA or protiens",
      "@type": "rdfs:Property",
      "rdfs:domain": [ "bio:Gene" ],
      "rdfs:range": [
        "bio:BioChemEntity",
        "bio:Protein",
        "schema:URL"
          ]
    },
    {"@id": "bio:hasRepresentation",
      "rdfs:label": "A common representation such as a protein sequence or chemical structure for this entity. For images use schema.org/image.",
      "@type": "rdfs:Property",
      "rdfs:domain": [ "bio:Gene"],
      "rdfs:range": [
        "schema:PropertyValue",
        "schema:Text",
        "schema:URL"
          ]
      },
    {"@id": "bio:isPartOfBioChemEntity",
      "rdfs:label": "Indicates a BioChemEntity that is (in some sense) a part of this BioChemEntity. Inverse property: hasBioChemEntity",
      "@type": "rdfs:Property",
      "rdfs:domain": [ "bio:Gene" ],
      "rdfs:range": [ "bio:BioChemEntity" ]
      },
    {"@id": "bio:associatedDisease",
      "rdfs:label": "Disease associated with this BioChemEntity",
      "@type": "rdfs:Property",
      "rdfs:domain": [],
      "rdfs:range": [
        ]
      },
    {"@id": "bio:hasBioChemEntityPart",
      "rdfs:label": "For genes, it can be used to link to gene sequence annotations such as variants or so.",
      "@type": "rdfs:Property",
      "rdfs:domain": [ "bio:Gene" ],
      "rdfs:range": [
          "bio:BioChemEntity"
        ]
      },
    {"@id": "bio:enablesMF",
      "rdfs:label": "",
      "@type": "rdfs:Property",
      "rdfs:domain": [ "bio:Gene" ],
      "rdfs:range": [
          "https://health-lifesci.schema.org/MedicalCondition",
          "schema:URL"
        ]
      },
    {"@id": "bio:hasCategoryCode",
      "rdfs:label": "A Category code contained in this code set.",
      "@type": "rdfs:Property",
      "rdfs:domain": [ "bio:Gene" ],
      "rdfs:range": [
          "https://pending.schema.org/CategoryCode"
        ]
      },
    {"@id": "bio:involvedInBP",
      "rdfs:label": "GO biological process this gene/protein is involved in. Recommended range: BioChemEntity or CategoryCode, ProteinAnnotation if evidence should be included. RO:0002331 (is involved in).",
      "@type": "rdfs:Property",
      "rdfs:domain": [ "bio:Gene" ],
      "rdfs:range": [
          "https://pending.schema.org/CategoryCode",
          "schema:PropertyValue"
        ]
      },
    {"@id": "bio:isTranscribedInto",
      "rdfs:label": "For genes, this property is used to link to gene products transcribed from this gene such as RNA. SIO:010080 (is transcribed into).",
      "@type": "rdfs:Property",
      "rdfs:domain": [ "bio:Gene"],
      "rdfs:range": [
          "bio:BioChemEntity"
        ]
      },
    {"@id": "bio:isVariantOf",
      "rdfs:label": "Use this property to express when a gene is a variant of any other gene. SIO: 000272 (is variant of). ",
      "@type": "rdfs:Property",
      "rdfs:domain": [ "Gene"],
      "rdfs:range": [
          "bio:BioChemEntity",
          "bio:Gene"
        ]
      },
    {"@id": "bio:taxonomicRange",
      "rdfs:label": "The taxonomic grouping of the organism that expresses, encodes, or in someway related to the BioChemEntity.",

      "@type": "rdfs:Property",
      "rdfs:domain": [ "bio:Gene" ],
      "rdfs:range": [
        "bio:Taxon",
        "schema:Text",
        "schema:URL"
        ]},
    {"@id": "bio:subjectOf",
      "@type": "rdfs:Property",
      "rdfs:subPropertyOf": "https://pending.schema.org/subjectOf",
      "rdfs:label": "Links to resources for (meta)data about this sample record.",
      "rdfs:domain": ["bio:Sample"],
      "rdfs:range": ["schema:CreativeWork", "schema:Event"]
      }
    ]

}
