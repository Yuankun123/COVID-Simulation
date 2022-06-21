'''class GeoRegion(AbstractRegion):

    """Every region is a parallelogram"""

    def __init__(self, name: str,
                 vcity: 'VirtualCity',
                 anchor1: np.ndarray,
                 extend_len: int,
                 extend_dir='horizontal',
                 anchor_mode='corner',
                 anchor2: np.ndarray = None,
                 targetable=True):
        """
        :param name: name of the region
        :param vcity: virtual city the region belongs to
        :param anchor1: anchor1 position
        :param extend_len: extend length
        :param extend_dir: horizontal or vertical
        :param anchor_mode: anchor's position related to the region, 'corner' or 'edge'
        :param anchor2: anchor2 position
        :param targetable: whether this region can become a target of transportation
        """
        super().__init__(name, targetable)
        self.vcity = vcity

        # configure the parallelogram region
        assert anchor_mode in ['corner', 'edge'], f'Bad parameter {anchor_mode} for anchor_mode'
        assert extend_dir in ['horizontal', 'vertical'], f'Bad parameter {extend_dir} for extend_dir'
        assert anchor1[0] <= anchor2[0] and anchor1[1] <= anchor2[1], f'{anchor1} is not on the lower left of {anchor2}'
        assert extend_len % 2 == 0, f'Extend length should be a even number'

        if anchor_mode == 'edge':
            if extend_dir == 'horizontal':
                sw_corner = anchor1 - np.array([extend_len / 2, 0])
            else:
                sw_corner = anchor1 - np.array([0, extend_len / 2])
        else:
            sw_corner = anchor1
        self.extend_dir = extend_dir
        self.extend_len = extend_len

        if extend_dir == 'horizontal':
            assert anchor2[1] != anchor1[1], 'Cannot extend horizontally because the anchors have the same y'
            self.main_dir_span = Span(anchor1[1], anchor2[1])
            ratio = (anchor2[0] - anchor1[0]) / self.main_dir_span.span
            self.get_subdir_span = lambda y: Span((y - sw_corner[1]) * ratio + sw_corner[0],
                                                  (y - sw_corner[1]) * ratio + sw_corner[0] + self.extend_len)
            main_cntr = self.main_dir_span.cntr
            self.cntr = np.array(self.get_subdir_span(main_cntr).cntr, main_cntr)
        else:
            assert anchor2[0] != anchor1[0], 'Cannot extend vertically because the anchors have the same x'
            self.main_dir_span = Span(anchor1[0], anchor2[0])
            ratio = (anchor2[1] - anchor1[1]) / self.main_dir_span.span
            self.get_subdir_span = lambda x: Span((x - sw_corner[0]) * ratio + sw_corner[1],
                                                  (x - sw_corner[0]) * ratio + sw_corner[1] + self.extend_len)
            main_cntr = self.main_dir_span.cntr
            self.cntr = np.array(main_cntr, self.get_subdir_span(main_cntr).cntr)

    def __contains__(self, pos: np.ndarray):
        if self.extend_dir == 'horizontal':
            if pos[1] in self.main_dir_span and pos[0] in self.get_subdir_span(pos[1]):
                return True
            else:
                return False
        else:
            if pos[0] in self.main_dir_span and pos[1] in self.get_subdir_span(pos[0]):
                return True
            else:
                return False

    def adjacent(self, pos: np.ndarray):
        """include both ends"""
        if self.extend_dir == 'horizontal':
            if self.main_dir_span.adjacent(pos[1]) and self.get_subdir_span(pos[1]).adjacent(pos[0]):
                return True
            else:
                return False
        else:
            if self.main_dir_span.adjacent(pos[0]) and self.get_subdir_span(pos[0]).adjacent(pos[1]):
                return True
            else:
                return False

    def rand_location(self) -> np.ndarray:
        main_sigma = self.main_dir_span.span / 6
        main_mu = self.main_dir_span.cntr
        random.seed(time.perf_counter())
        main_val = random.gauss(main_mu, main_sigma)
        while main_val not in self.main_dir_span:
            main_val = random.gauss(main_mu, main_sigma)

        current_sub_span = self.get_subdir_span(main_val)
        sub_sigma = current_sub_span.span / 6
        sub_mu = current_sub_span.cntr
        random.seed(time.perf_counter())
        sub_val = random.gauss(sub_mu, sub_sigma)
        while sub_val not in current_sub_span:
            sub_val = random.gauss(sub_mu, sub_sigma)

        if self.extend_dir == 'horizontal':
            return np.array(sub_val, main_val)
        else:
            return np.array(main_val, sub_val)'''