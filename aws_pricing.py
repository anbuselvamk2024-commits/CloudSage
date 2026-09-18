import boto3
import json


def get_ec2_price(instance_type):

    pricing = boto3.client(
        "pricing",
        region_name="ap-south-1"
    )

    response = pricing.get_products(
        ServiceCode="AmazonEC2",
        Filters=[
            {
                "Type": "TERM_MATCH",
                "Field": "instanceType",
                "Value": instance_type
            },
            {
                "Type": "TERM_MATCH",
                "Field": "location",
                "Value": "Asia Pacific (Mumbai)"
            },
            {
                "Type": "TERM_MATCH",
                "Field": "operatingSystem",
                "Value": "Linux"
            },
            {
                "Type": "TERM_MATCH",
                "Field": "tenancy",
                "Value": "Shared"
            },
            {
                "Type": "TERM_MATCH",
                "Field": "preInstalledSw",
                "Value": "NA"
            },
            {
                "Type": "TERM_MATCH",
                "Field": "capacitystatus",
                "Value": "Used"
            }
        ],
        MaxResults=1
    )

    if not response["PriceList"]:
        return None

    product = json.loads(response["PriceList"][0])

    on_demand = product["terms"]["OnDemand"]

    first_term = next(iter(on_demand.values()))

    price_dimensions = first_term["priceDimensions"]

    first_dimension = next(iter(price_dimensions.values()))

    hourly_price = float(
        first_dimension["pricePerUnit"]["USD"]
    )

    monthly_price = hourly_price * 24 * 30

    return {
        "instance_type": instance_type,
        "hourly_usd": round(hourly_price, 6),
        "monthly_usd": round(monthly_price, 2)
    }


if __name__ == "__main__":

    for instance in [
        "t3.nano",
        "t3.micro",
        "t3.small"
    ]:

        print(get_ec2_price(instance))