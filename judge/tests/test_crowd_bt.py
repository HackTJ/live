from django.test import TestCase
from judge.crowd_bt import (
    divergence_gaussian,
    divergence_beta,
)


class CreateSecretsTest(TestCase):
    def test_divergence_gaussian(self):
        pass

    def test_divergence_beta(self):
        # https://en.wikipedia.org/wiki/Beta_distribution#cite_ref-Cover_and_Thomas_30-1:~:text=The%20relative%20entropy%2C%20or%20Kullback%E2%80%93Leibler%20divergence%2C,h(X1)%20%3D%20%E2%88%921.10805%3B%20h(X2)%20%3D%20%E2%88%921.10805.

        self.assertAlmostEqual(divergence_beta(1.0, 1.0, 3.0, 3.0), 0.598803, places=6)
        self.assertAlmostEqual(divergence_beta(3.0, 3.0, 1.0, 1.0), 0.267864)

        self.assertAlmostEqual(divergence_beta(3.0, 0.5, 0.5, 3.0), 7.21574, places=5)
        self.assertAlmostEqual(divergence_beta(0.5, 3.0, 3.0, 0.5), 7.21574, places=5)
