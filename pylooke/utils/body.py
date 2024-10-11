from typing import Optional

def get_groups(extras: Optional[dict] = None) -> list:
    groups = [
        {
            "GroupName": "SerieInfo",
            "GroupProperties": "EpisodeName|Position|SeasonName"
        },
        {
            "GroupName": "Metadata",
            "GroupProperties": (
                "Actors|AverageRating|Censure|Country|Description|"
                "Directors|Distributor|Genres|IsCinema|PreOrderDate|"
                "Synopsis|TrailerUrl|UniqueUrl|Year"
            )
        },
        {
            "GroupName": "FileInfo",
            "GroupProperties": (
                "Audios|CreditStartsAt|Definition|DubbedInfo|Duration|"
                "RestrictDownloadBrazil|RestrictDownloadBuy|"
                "RestrictDownloadRent|RestrictDownloadSVOD|Subtitles"
            )
        },
        {
            "GroupName": "Smooth",
            "GroupProperties": "TimeFrameDistance|TimeFrameUrl|UrlDashStreaming"
        },
        {
            "GroupName": "Images",
            "GroupProperties": "TypeId|Url"
        },
        {
            "GroupName": "Price",
            "GroupProperties": "FreePrice|PreOrder|PurchasePrice|RentPrice|SVODPrice"
        }
    ]

    if extras:
        groups.append(extras)

    return groups

def get_entities(extras: Optional[dict] = None) -> list:
    entities = [
        {
            "EntityName": "Subtitles",
            "EntityProperties": "UrlVTT|UrlTTM|UrlSRT|Name|Code"
        }
    ]

    if extras:
        entities.append(extras)

    return entities

def get_options(extras: Optional[dict] = None) -> dict:
    options = {
        "BoxBehavior": "Group",
        "FillSiblings": False,
        "FillSiblingsChilds": False,
        "ImageTypeIds": [-1, 4001, 9001, 9011],
        "IncludeCinemaItens": True,
        "IncludeNullPriceItens": False,
        "IncludePreOrderItens": True,
        "OnlyEnabledItens": True,
        "OnlySVODItens": False,
        "PageNumber": 0,
        "RecordsPerPage": 50,
        "SortCriteria": "None",
        "SortOrder": "DESC",
        "UseApplePriceBRL": False
    }

    if extras:
        options.update(extras)

    return options