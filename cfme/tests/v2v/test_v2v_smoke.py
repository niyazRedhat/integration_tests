"""Test to validate End-to-End migrations- functional testing."""
import fauxfactory
import pytest

from cfme import test_requirements
from cfme.cloud.provider.openstack import OpenStackProvider
from cfme.fixtures.provider import rhel7_minimal
from cfme.fixtures.v2v_fixtures import get_migrated_vm
from cfme.infrastructure.provider.rhevm import RHEVMProvider
from cfme.infrastructure.provider.virtualcenter import VMwareProvider
from cfme.markers.env_markers.provider import ONE_PER_VERSION


pytestmark = [
    test_requirements.v2v,
    pytest.mark.provider(
        classes=[RHEVMProvider, OpenStackProvider],
        selector=ONE_PER_VERSION,
        required_flags=["v2v"],
        scope="module",
    ),
    pytest.mark.provider(
        classes=[VMwareProvider],
        selector=ONE_PER_VERSION,
        fixture_name="source_provider",
        required_flags=["v2v"],
        scope="module",
    ),
    pytest.mark.usefixtures("v2v_provider_setup"),
]


@pytest.mark.parametrize(
    "v2v_provider_setup, mapping_data_multiple_vm_obj_single_datastore",
    [
        [
            "SSH", ["nfs", "nfs", [rhel7_minimal]]
        ],
        [
            "VDDK", ["nfs", "nfs", [rhel7_minimal]]
        ]
    ],
    indirect=True,
)
def test_single_vm_migration_with_ssh_and_vddk(
    request, appliance, provider, mapping_data_multiple_vm_obj_single_datastore
):
    """
    Polarion:
        assignee: sshveta
        caseimportance: high
        caseposneg: positive
        testtype: functional
        startsin: 5.10
        casecomponent: V2V
        initialEstimate: 1h
    """
    infrastructure_mapping_collection = appliance.collections.v2v_infra_mappings
    mapping_data = mapping_data_multiple_vm_obj_single_datastore.infra_mapping_data
    mapping = infrastructure_mapping_collection.create(**mapping_data)

    @request.addfinalizer
    def _cleanup():
        infrastructure_mapping_collection.delete(mapping)

    migration_plan_collection = appliance.collections.v2v_migration_plans
    migration_plan = migration_plan_collection.create(
        name="plan_{}".format(fauxfactory.gen_alphanumeric()),
        description="desc_{}".format(fauxfactory.gen_alphanumeric()),
        infra_map=mapping.name,
        target_provider=provider,
        vm_list=mapping_data_multiple_vm_obj_single_datastore.vm_list,
    )

    assert migration_plan.wait_for_state("Started")
    assert migration_plan.wait_for_state("In_Progress")
    assert migration_plan.wait_for_state("Completed")
    assert migration_plan.wait_for_state("Successful")

    # validate MAC address matches between source and target VMs
    src_vm = mapping_data_multiple_vm_obj_single_datastore.vm_list.pop()
    migrated_vm = get_migrated_vm(src_vm, provider)
    assert src_vm.mac_address == migrated_vm.mac_address