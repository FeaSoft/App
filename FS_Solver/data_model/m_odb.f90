! Description:
! Definition of an output database.
module m_odb
    implicit none
    
    private
    public t_odb, new_odb
    
    type t_odb
        integer :: size                                 ! current storage size
        integer :: n_frames                             ! current number of frames
        integer :: n_nodes                              ! number of mesh nodes
        integer :: n_hout                               ! number of history outputs
        integer :: n_nsfout                             ! number of nodal scalar field outputs
        character(64), allocatable :: d_frames(:)       ! description of frames
        character(64), allocatable :: d_hout(:)         ! description of history outputs
        character(64), allocatable :: d_nsfout(:)       ! description of nodal scalar field outputs
        real,          allocatable :: v_hout(:, :)      ! values of history outputs
        real,          allocatable :: v_nsfout(:, :, :) ! values of nodal scalar field outputs
    contains
        procedure :: set_nsfout_descr, set_hout_descr, set_nsfout, set_hout, new_frame, squeeze
        final     :: destructor
    end type
    
    interface new_odb
        module procedure :: constructor
    end interface
    
    contains
    
    ! Description:
    ! Output database constructor.
    type(t_odb) function constructor(n_nodes, n_hout, n_nsfout) result(self)
        integer, intent(in) :: n_nodes  ! number of mesh nodes
        integer, intent(in) :: n_hout   ! number of history outputs
        integer, intent(in) :: n_nsfout ! number of nodal scalar field outputs
        self%size     = 1
        self%n_frames = 0
        self%n_nodes  = n_nodes
        self%n_hout   = n_hout
        self%n_nsfout = n_nsfout
        allocate(self%d_frames(self%size                             ))
        allocate(self%d_hout  (self%n_hout                           ))
        allocate(self%d_nsfout(self%n_nsfout                         ))
        allocate(self%v_hout  (self%size, self%n_hout                ))
        allocate(self%v_nsfout(self%size, self%n_nsfout, self%n_nodes))
    end function
    
    ! Description:
    ! Output database destructor.
    subroutine destructor(self)
        type(t_odb), intent(inout) :: self
        if (allocated(self%d_frames)) deallocate(self%d_frames)
        if (allocated(self%d_hout  )) deallocate(self%d_hout  )
        if (allocated(self%d_nsfout)) deallocate(self%d_nsfout)
        if (allocated(self%v_hout  )) deallocate(self%v_hout  )
        if (allocated(self%v_nsfout)) deallocate(self%v_nsfout)
    end subroutine
    
    ! Description:
    ! Sets the nodal scalar field output description.
    subroutine set_nsfout_descr(self, index, description)
        class(t_odb), intent(inout) :: self
        character(*), intent(in)    :: description
        integer,      intent(in)    :: index
        self%d_nsfout(index) = description
    end subroutine
    
    ! Description:
    ! Sets the history output description.
    subroutine set_hout_descr(self, index, description)
        class(t_odb), intent(inout) :: self
        character(*), intent(in)    :: description
        integer,      intent(in)    :: index
        self%d_hout(index) = description
    end subroutine
    
    ! Description:
    ! Creates a new output frame.
    integer function new_frame(self, description) result(frame)
        class(t_odb), intent(inout) :: self
        character(*), intent(in)    :: description
        
        ! allocate more storage if required
        if (self%n_frames == self%size) call resize(self, self%size*2)
        
        ! store description and return frame index
        self%n_frames = self%n_frames + 1
        self%d_frames(self%n_frames) = description
        frame = self%n_frames
    end function
    
    ! Description:
    ! Stores the specified nodal scalar field output.
    subroutine set_nsfout(self, frame, index, values)
        class(t_odb), intent(inout) :: self
        integer,      intent(in)    :: frame
        integer,      intent(in)    :: index
        real,         intent(in)    :: values(:)
        self%v_nsfout(frame, index, :) = values(:)
    end subroutine
    
    ! Description:
    ! Stores the specified history output.
    subroutine set_hout(self, frame, index, value)
        class(t_odb), intent(inout) :: self
        integer,      intent(in)    :: frame
        integer,      intent(in)    :: index
        real,         intent(in)    :: value
        self%v_hout(frame, index) = value
    end subroutine
    
    ! Description:
    ! Removes excess storage.
    subroutine squeeze(self)
        class(t_odb), intent(inout) :: self
        call resize(self, self%n_frames)
    end subroutine
    
    ! Description:
    ! Resizes the storage arrays.
    subroutine resize(odb, new_size)
        type(t_odb),   intent(inout) :: odb
        integer,       intent(in)    :: new_size
        character(64), allocatable   :: new_d_frames(:)
        real,          allocatable   :: new_v_hout(:, :)
        real,          allocatable   :: new_v_nsfout(:, :, :)
        
        if (new_size /= odb%size) then
        
            ! allocate new arrays
            allocate(new_d_frames(new_size                           ))
            allocate(new_v_hout  (new_size, odb%n_hout               ))
            allocate(new_v_nsfout(new_size, odb%n_nsfout, odb%n_nodes))
        
            ! copy old values to new arrays
            if (new_size > odb%size) then
                new_d_frames(1:odb%size      ) = odb%d_frames
                new_v_hout  (1:odb%size, :   ) = odb%v_hout
                new_v_nsfout(1:odb%size, :, :) = odb%v_nsfout
            else
                new_d_frames = odb%d_frames(1:new_size      )
                new_v_hout   = odb%v_hout  (1:new_size, :   )
                new_v_nsfout = odb%v_nsfout(1:new_size, :, :)
            end if
        
            ! swap old by new arrays
            call move_alloc(new_d_frames, odb%d_frames)
            call move_alloc(new_v_hout,   odb%v_hout  )
            call move_alloc(new_v_nsfout, odb%v_nsfout)
        
            ! update size info
            odb%size = new_size
        
        end if
    end subroutine
    
end module
