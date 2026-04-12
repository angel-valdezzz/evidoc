*** Settings ***
Library    evidoc.robot
Library    examples.robot.support.SupportLibrary

*** Test Cases ***
Capture Evidence With Evidoc
    ${artifact_path}=    Create Demo Artifact    ${OUTPUT DIR}${/}sample.txt
    ${driver}=    Get Demo Driver
    Log Step    Open checkout    PASS
    Log Info    Entering checkout flow
    Attach Artifact    ${artifact_path}    Input fixture used by the test
    Capture Screenshot    driver=${driver}    title=Checkout page    description=Before submit
    Log Warning    Checkout is slower than expected
    Log Error    Validation summary example
