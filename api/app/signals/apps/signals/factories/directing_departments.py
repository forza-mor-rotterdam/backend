from factory import DjangoModelFactory, Sequence, SubFactory, post_generation

from signals.apps.signals.models import SignalDepartments


class DirectingDepartmentsFactory(DjangoModelFactory):
    class Meta:
        model = SignalDepartments

    _signal = SubFactory('signals.apps.signals.factories.signal.SignalFactory', category_assignment=None)
    created_by = Sequence(lambda n: 'beheerder{}@example.com'.format(n))
    relation_type = 'directing'

    @post_generation
    def set_one_to_one_relation(self, create, extracted, **kwargs):
        self.signal = self._signal

    @post_generation
    def departments(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            # A list of groups were passed in, use them
            for department in extracted:
                self.departments.add(department)
